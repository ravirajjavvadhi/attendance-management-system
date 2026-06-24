package com.example.eduflowsmsgateway

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.example.eduflowsmsgateway.theme.EduFlowSMSGatewayTheme
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    private val viewModel: GatewayViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Start the background SMS polling service
        val serviceIntent = Intent(this, SmsPollingService::class.java)
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
            startForegroundService(serviceIntent)
        } else {
            startService(serviceIntent)
        }

        // Enqueue Heartbeat Worker
        val heartbeatWorkRequest = androidx.work.PeriodicWorkRequestBuilder<HeartbeatWorker>(15, java.util.concurrent.TimeUnit.MINUTES)
            .build()
        androidx.work.WorkManager.getInstance(this).enqueueUniquePeriodicWork(
            "HeartbeatWorker",
            androidx.work.ExistingPeriodicWorkPolicy.KEEP,
            heartbeatWorkRequest
        )

        setContent {
            EduFlowSMSGatewayTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    val isPaired by viewModel.isPaired.collectAsStateWithLifecycle()
                    
                    if (isPaired) {
                        DashboardScreen(
                            onUnpair = { viewModel.unpairDevice() }
                        )
                    } else {
                        PairingScreen(viewModel = viewModel)
                    }
                }
            }
        }
    }
}

@Composable
fun PairingScreen(viewModel: GatewayViewModel) {
    var tokenInput by remember { mutableStateOf("") }
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("EduFlow Gateway", fontSize = 28.sp, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
        Spacer(modifier = Modifier.height(8.dp))
        Text("Enter the 6-digit pairing code from your web dashboard to connect this device.", textAlign = TextAlign.Center, color = MaterialTheme.colorScheme.onSurfaceVariant)
        
        Spacer(modifier = Modifier.height(32.dp))

        OutlinedTextField(
            value = tokenInput,
            onValueChange = { if (it.length <= 6) tokenInput = it },
            label = { Text("Pairing Code") },
            singleLine = true,
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(24.dp))

        Button(
            onClick = { viewModel.pairDevice(tokenInput) },
            modifier = Modifier.fillMaxWidth().height(50.dp),
            enabled = tokenInput.length == 6 && uiState !is GatewayViewModel.UiState.Loading
        ) {
            if (uiState is GatewayViewModel.UiState.Loading) {
                CircularProgressIndicator(modifier = Modifier.size(24.dp), color = MaterialTheme.colorScheme.onPrimary)
            } else {
                Text("Pair Device")
            }
        }

        if (uiState is GatewayViewModel.UiState.Error) {
            Spacer(modifier = Modifier.height(16.dp))
            Text((uiState as GatewayViewModel.UiState.Error).message, color = MaterialTheme.colorScheme.error)
        }
    }
}

@Composable
fun DashboardScreen(viewModel: GatewayViewModel, onUnpair: () -> Unit) {
    val pendingCount by viewModel.pendingCount.collectAsStateWithLifecycle(initialValue = 0)
    val sentCount by viewModel.sentCount.collectAsStateWithLifecycle(initialValue = 0)
    val failedCount by viewModel.failedCount.collectAsStateWithLifecycle(initialValue = 0)

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("Gateway Active", fontSize = 28.sp, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
        Spacer(modifier = Modifier.height(16.dp))
        Text("This device is successfully paired and actively polling.", textAlign = TextAlign.Center)
        
        Spacer(modifier = Modifier.height(32.dp))

        // Diagnostic Metrics Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Diagnostic Mode (Local Room DB)", fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.height(8.dp))
                Text("Messages in Local Queue: $pendingCount")
                Text("Successfully Dispatched: $sentCount", color = androidx.compose.ui.graphics.Color(0xFF2E7D32))
                Text("Failed Dispatches: $failedCount", color = MaterialTheme.colorScheme.error)
            }
        }

        Spacer(modifier = Modifier.height(48.dp))

        Button(
            onClick = onUnpair,
            colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.error)
        ) {
            Text("Unpair Device")
        }
    }
}
