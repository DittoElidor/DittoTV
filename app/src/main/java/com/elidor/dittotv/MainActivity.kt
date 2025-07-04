package com.elidor.dittotv

import android.annotation.SuppressLint
import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.webkit.JavascriptInterface
import android.webkit.WebView
import android.webkit.WebViewClient

class MainActivity : Activity() {

    private lateinit var myWebView: WebView
    private var currentWebView = "main"
    private val VIDEO_PLAYER_REQUEST_CODE = 1001

    companion object {
        private const val SERVER_BASE_URL = "http://10.100.102.10:8000"
    }

    @SuppressLint("SetJavaScriptEnabled", "AddJavascriptInterface")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        myWebView = findViewById(R.id.webview)
        myWebView.settings.javaScriptEnabled = true
        myWebView.settings.domStorageEnabled = true
        myWebView.webViewClient = WebViewClient()
        myWebView.addJavascriptInterface(WebAppInterface(this), "DittoTVInterface")
        myWebView.loadUrl("$SERVER_BASE_URL/web/")
    }

    override fun onResume() {
        super.onResume()
        myWebView.evaluateJavascript("javascript:renderMainView();", null)
    }

    override fun onBackPressed() {
        if (currentWebView == "detail") {
            myWebView.evaluateJavascript("javascript:goBack();", null)
        } else {
            super.onBackPressed()
        }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == VIDEO_PLAYER_REQUEST_CODE && resultCode == RESULT_OK) {
            val path = data?.getStringExtra("relativePath")
            val position = data?.getLongExtra("position", 0)
            val duration = data?.getLongExtra("duration", 0)
            if (path != null && position != null && duration != null) {
                val safePath = path.replace("'", "\\'")
                val script = "javascript:saveProgress('${safePath}', ${position}, ${duration});"
                myWebView.evaluateJavascript(script, null)
            }
        }
    }

    inner class WebAppInterface(private val mContext: Activity) {
        @JavascriptInterface
        fun playVideo(fullUrl: String) {
            val relativePath = fullUrl.substring(fullUrl.indexOf("media/"))
            val intent = Intent(mContext, VideoPlayerActivity::class.java).apply {
                putExtra("videoUrl", fullUrl)
                putExtra("relativePath", relativePath)
            }
            mContext.startActivityForResult(intent, VIDEO_PLAYER_REQUEST_CODE)
        }

        @JavascriptInterface
        fun playVideoFrom(relativePath: String, position: Long) {
            val fullUrl = "$SERVER_BASE_URL/$relativePath"
            val intent = Intent(mContext, VideoPlayerActivity::class.java).apply {
                putExtra("videoUrl", fullUrl)
                putExtra("relativePath", relativePath)
                putExtra("startPosition", position)
            }
            mContext.startActivityForResult(intent, VIDEO_PLAYER_REQUEST_CODE)
        }

        @JavascriptInterface
        fun onViewChanged(viewName: String) {
            currentWebView = viewName
        }
    }
}
