package com.stealthguard

import android.Manifest
import android.app.Activity
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebView
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.core.content.ContextCompat
import com.stealthguard.ui.StealthGuardWebView

class MainActivity : ComponentActivity() {
    
    // Replace with your actual Vercel URL
    private val webUrl = "https://stealthguard-v2.vercel.app"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        setContent {
            MaterialTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    var webView by remember { mutableStateOf<WebView?>(null) }
                    var filePathCallback by remember { mutableStateOf<ValueCallback<Array<Uri>>?>(null) }

                    val fileChooserLauncher = rememberLauncherForActivityResult(
                        contract = ActivityResultContracts.StartActivityForResult()
                    ) { result ->
                        if (result.resultCode == Activity.RESULT_OK) {
                            val data = result.data
                            val uris = WebChromeClient.FileChooserParams.parseResult(result.resultCode, data)
                            filePathCallback?.onReceiveValue(uris)
                        } else {
                            filePathCallback?.onReceiveValue(null)
                        }
                        filePathCallback = null
                    }

                    val requestPermissionLauncher = rememberLauncherForActivityResult(
                        ActivityResultContracts.RequestPermission()
                    ) { isGranted ->
                        if (!isGranted) {
                            Toast.makeText(this, "Notification permission is required for download alerts", Toast.LENGTH_SHORT).show()
                        }
                    }

                    LaunchedEffect(Unit) {
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                            if (ContextCompat.checkSelfPermission(this@MainActivity, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                                requestPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
                            }
                        }
                    }

                    BackHandler(enabled = webView?.canGoBack() == true) {
                        webView?.goBack()
                    }

                    val webViewProvider = remember { mutableStateOf<WebView?>(null) }
                    webView = webViewProvider.value

                    StealthGuardWebView(
                        url = webUrl,
                        webViewProvider = webViewProvider,
                        onFilePickerShow = { callback, params ->
                            filePathCallback = callback
                            val intent = params?.createIntent()
                            if (intent != null) {
                                fileChooserLauncher.launch(intent)
                            } else {
                                filePathCallback?.onReceiveValue(null)
                                filePathCallback = null
                            }
                        }
                    )
                }
            }
        }
    }
}
