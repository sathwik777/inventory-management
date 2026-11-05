<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <template v-else>
      <!-- Budget Card -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.budget') }}</h3>
        </div>
        <div class="budget-control">
          <div class="budget-display">
            <span class="budget-current">{{ formatCurrency(sliderBudget, currentCurrency) }}</span>
            <span class="budget-sub-label">{{ t('restocking.availableBudget') }}</span>
          </div>
          <div class="slider-row">
            <span class="slider-end-label">{{ formatCurrency(0, currentCurrency) }}</span>
            <input
              type="range"
              class="budget-slider"
              :min="0"
              :max="maxBudget"
              step="100"
              :value="sliderBudget"
              @input="onBudgetInput"
              @change="onBudgetChange"
            />
            <span class="slider-end-label">{{ formatCurrency(maxBudget, currentCurrency) }}</span>
          </div>
        </div>
      </div>

      <!-- Candidates Table -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.table.candidates') }}</h3>
        </div>
        <div v-if="reloadingRecs" class="loading">{{ t('common.loading') }}</div>
        <div v-else-if="recsError" class="error">{{ recsError }}</div>
        <div v-else-if="candidates.length === 0" class="empty-state">{{ t('restocking.noCandidates') }}</div>
        <div v-else class="table-container">
          <table class="candidates-table">
            <thead>
              <tr>
                <th class="col-select"></th>
                <th class="col-sku">{{ t('restocking.table.sku') }}</th>
                <th class="col-product">{{ t('restocking.table.product') }}</th>
                <th class="col-category">{{ t('restocking.table.category') }}</th>
                <th class="col-trend">{{ t('restocking.table.trend') }}</th>
                <th class="col-qty">{{ t('restocking.table.quantity') }}</th>
                <th class="col-cost">{{ t('restocking.table.unitCost') }}</th>
                <th class="col-total">{{ t('restocking.table.lineTotal') }}</th>
                <th class="col-lead">{{ t('restocking.table.leadTime') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="candidate in candidates" :key="candidate.sku">
                <td class="col-select">
                  <input
                    type="checkbox"
                    :checked="selectedMap[candidate.sku] === true"
                    @change="toggleCandidate(candidate)"
                  />
                </td>
                <td class="col-sku"><strong>{{ candidate.sku }}</strong></td>
                <td class="col-product">{{ translateProductName(candidate.name) }}</td>
                <td class="col-category">{{ translateCategory(candidate.category) }}</td>
                <td class="col-trend">
                  <span :class="['badge', candidate.trend]">
                    {{ t(`trends.${candidate.trend}`) }}
                  </span>
                </td>
                <td class="col-qty">{{ candidate.quantity }}</td>
                <td class="col-cost">{{ formatMoney(candidate.unit_cost) }}</td>
                <td class="col-total">{{ formatMoney(candidate.line_total) }}</td>
                <td class="col-lead">{{ candidate.lead_time_days }} {{ t('restocking.days') }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Summary and Order -->
      <div class="card summary-card">
        <div class="summary-grid">
          <div class="summary-item">
            <span class="summary-label">{{ t('restocking.selectedTotal') }}</span>
            <span class="summary-value">{{ formatMoney(selectedTotal) }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">{{ t('restocking.remaining') }}</span>
            <span class="summary-value" :class="{ 'over-budget-text': remainingBudget < 0 }">
              {{ formatMoney(remainingBudget) }}
            </span>
          </div>
          <div class="summary-item">
            <span class="summary-label">{{ t('restocking.leadTime') }}</span>
            <span class="summary-value">{{ orderLeadTime }}</span>
          </div>
        </div>

        <div v-if="successMessage" class="success-message">
          {{ successMessage }}
          <router-link to="/orders" class="orders-link">{{ t('restocking.viewOrders') }}</router-link>
        </div>
        <div v-if="orderError" class="error order-error">{{ orderError }}</div>

        <button
          class="btn-primary"
          :disabled="!canPlaceOrder"
          @click="placeOrder"
        >
          {{ orderInProgress ? t('restocking.placing') : t('restocking.placeOrder') }}
        </button>
      </div>
    </template>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'
import { formatCurrency, formatCurrencyWithDecimals } from '../utils/currency'

export default {
  name: 'Restocking',
  setup() {
    const { t, currentCurrency, translateProductName } = useI18n()

    const loading = ref(true)
    const error = ref(null)
    const reloadingRecs = ref(false)
    const recsError = ref(null)
    const candidates = ref([])
    const maxBudget = ref(0)
    const sliderBudget = ref(0)
    const selectedMap = ref({})
    const orderInProgress = ref(false)
    const orderError = ref(null)
    const successMessage = ref(null)

    let latestRequest = 0

    const applyRecommendations = (data) => {
      maxBudget.value = data.max_budget
      candidates.value = data.candidates
      const map = {}
      data.candidates.forEach(c => {
        if (c.recommended) map[c.sku] = true
      })
      selectedMap.value = map
    }

    const loadRecommendations = async (budget, isInitial = false) => {
      if (isInitial) {
        loading.value = true
        error.value = null
      } else {
        reloadingRecs.value = true
      }
      recsError.value = null
      const requestId = ++latestRequest
      try {
        const data = await api.getRestockRecommendations(budget)
        // Ignore responses that a newer slider change has replaced.
        if (requestId !== latestRequest) return
        if (isInitial) sliderBudget.value = data.budget
        applyRecommendations(data)
      } catch (err) {
        if (requestId !== latestRequest) return
        const message = 'Failed to load recommendations: ' + err.message
        if (isInitial) {
          error.value = message
        } else {
          recsError.value = message
        }
      } finally {
        if (requestId === latestRequest) {
          loading.value = false
          reloadingRecs.value = false
        }
      }
    }

    const onBudgetInput = (e) => {
      sliderBudget.value = Number(e.target.value)
    }

    const onBudgetChange = (e) => {
      successMessage.value = null
      orderError.value = null
      loadRecommendations(Number(e.target.value))
    }

    const formatMoney = (amount) => formatCurrencyWithDecimals(amount, currentCurrency.value, 2)

    const translateCategory = (category) => {
      const categoryMap = {
        'Circuit Boards': t('categories.circuitBoards'),
        'Sensors': t('categories.sensors'),
        'Actuators': t('categories.actuators'),
        'Controllers': t('categories.controllers'),
        'Power Supplies': t('categories.powerSupplies')
      }
      return categoryMap[category] || category
    }

    const toggleCandidate = (candidate) => {
      const map = { ...selectedMap.value }
      if (map[candidate.sku]) {
        delete map[candidate.sku]
      } else {
        map[candidate.sku] = true
      }
      selectedMap.value = map
    }

    const selectedCandidates = computed(() =>
      candidates.value.filter(c => selectedMap.value[c.sku] === true)
    )

    const selectedTotal = computed(() =>
      selectedCandidates.value.reduce((sum, c) => sum + c.line_total, 0)
    )

    const remainingBudget = computed(() => sliderBudget.value - selectedTotal.value)

    const orderLeadTime = computed(() => {
      if (selectedCandidates.value.length === 0) return '-'
      const max = Math.max(...selectedCandidates.value.map(c => c.lead_time_days))
      return `${max} ${t('restocking.days')}`
    })

    const canPlaceOrder = computed(() =>
      selectedCandidates.value.length > 0 &&
      remainingBudget.value >= 0 &&
      !orderInProgress.value &&
      !reloadingRecs.value
    )

    const placeOrder = async () => {
      if (!canPlaceOrder.value) return
      orderInProgress.value = true
      orderError.value = null
      successMessage.value = null
      try {
        const result = await api.createRestockOrder({
          budget: sliderBudget.value,
          items: selectedCandidates.value.map(c => ({ sku: c.sku, quantity: c.quantity }))
        })
        successMessage.value = t('restocking.success', { orderNumber: result.order_number })
        await loadRecommendations(sliderBudget.value)
      } catch (err) {
        const detail = err.response?.data?.detail
        orderError.value = detail || ('Failed to place order: ' + err.message)
      } finally {
        orderInProgress.value = false
      }
    }

    onMounted(() => loadRecommendations(undefined, true))

    return {
      t,
      currentCurrency,
      translateProductName,
      formatCurrency,
      formatMoney,
      loading,
      error,
      reloadingRecs,
      recsError,
      translateCategory,
      candidates,
      maxBudget,
      sliderBudget,
      selectedMap,
      onBudgetInput,
      onBudgetChange,
      toggleCandidate,
      selectedTotal,
      remainingBudget,
      orderLeadTime,
      canPlaceOrder,
      orderInProgress,
      orderError,
      successMessage,
      placeOrder
    }
  }
}
</script>

<style scoped>
.budget-control {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.5rem 0;
}

.budget-display {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
}

.budget-current {
  font-size: 2rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.025em;
}

.budget-sub-label {
  font-size: 0.875rem;
  color: #64748b;
}

.slider-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.slider-end-label {
  font-size: 0.813rem;
  color: #64748b;
  white-space: nowrap;
  flex-shrink: 0;
}

.budget-slider {
  -webkit-appearance: none;
  appearance: none;
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: #e2e8f0;
  outline: none;
  cursor: pointer;
}

.budget-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #0f172a;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.budget-slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #0f172a;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  border: none;
}

.candidates-table {
  table-layout: fixed;
  width: 100%;
}

.col-select {
  width: 36px;
}

.col-sku {
  width: 100px;
}

.col-product {
  width: 200px;
}

.col-category {
  width: 120px;
}

.col-trend {
  width: 100px;
}

.col-qty {
  width: 80px;
}

.col-cost {
  width: 100px;
}

.col-total {
  width: 110px;
}

.col-lead {
  width: 100px;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #64748b;
  font-size: 0.938rem;
}

.summary-card .summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.25rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid #e2e8f0;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.summary-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.summary-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.025em;
}

.over-budget-text {
  color: #dc2626;
}

.success-message {
  background: #d1fae5;
  border: 1px solid #6ee7b7;
  color: #065f46;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.orders-link {
  color: #059669;
  font-weight: 600;
  text-decoration: underline;
  white-space: nowrap;
}

.order-error {
  margin-bottom: 1rem;
}

.btn-primary {
  background: #0f172a;
  color: white;
  border: none;
  padding: 0.625rem 1.5rem;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background: #1e293b;
}

.btn-primary:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}
</style>
