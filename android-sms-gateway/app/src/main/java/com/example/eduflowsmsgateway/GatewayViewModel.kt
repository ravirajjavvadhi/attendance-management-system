package com.example.eduflowsmsgateway

import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.eduflowsmsgateway.api.ApiClient
import com.example.eduflowsmsgateway.api.RegisterDeviceRequest
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
class GatewayViewModel(
    private val sessionManager: SessionManager,
    private val smsDao: com.example.eduflowsmsgateway.data.SmsDao
) : ViewModel() {

    private val _isPaired = MutableStateFlow(sessionManager.isPaired())
    val isPaired: StateFlow<Boolean> = _isPaired.asStateFlow()

    private val _uiState = MutableStateFlow<UiState>(UiState.Idle)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    val pendingCount = smsDao.getPendingCountFlow()
    val sentCount = smsDao.getSentCountFlow()
    val failedCount = smsDao.getFailedCountFlow()

    fun pairDevice(pairingToken: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                val request = RegisterDeviceRequest(
                    pairingToken = pairingToken,
                    deviceUuid = sessionManager.getDeviceUuid()
                )
                val response = ApiClient.apiService.registerDevice(request)
                
                if (response.isSuccessful && response.body() != null) {
                    val token = response.body()!!.accessToken
                    sessionManager.saveAuthToken(token)
                    _isPaired.value = true
                    _uiState.value = UiState.Success("Paired Successfully!")
                } else {
                    _uiState.value = UiState.Error("Invalid Token or Device already paired.")
                }
            } catch (e: Exception) {
                Log.e("GatewayViewModel", "Pairing error", e)
                _uiState.value = UiState.Error(e.localizedMessage ?: "Network error")
            }
        }
    }

    fun unpairDevice() {
        sessionManager.clearAuthToken()
        _isPaired.value = false
    }

    sealed class UiState {
        object Idle : UiState()
        object Loading : UiState()
        data class Success(val message: String) : UiState()
        data class Error(val message: String) : UiState()
    }
}
