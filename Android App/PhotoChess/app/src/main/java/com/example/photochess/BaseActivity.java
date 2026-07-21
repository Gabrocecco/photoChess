package com.example.photochess;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Build;

import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

/**
 * Chrome and Python-VM-startup helpers shared by MainActivity,
 * CameraActivity and AnalyzeActivity, factored out of what used to be
 * three copies of the same few lines (see git history).
 *
 * Deliberately does NOT override onCreate(): all three activities call
 * getSupportActionBar() only after their own setContentView(), and
 * AppCompatActivity.getSupportActionBar() needs the content view already
 * installed. A base-class onCreate() runs via super.onCreate() at the top
 * of a subclass's onCreate(), i.e. before that subclass's setContentView()
 * — which would silently reorder these calls and risk a
 * NullPointerException, something there was no way to verify one way or
 * the other without a real Android build (see CLAUDE.md's Fase 3 caveat,
 * which applies here too). Subclasses call applyPhotoChessChrome() and
 * ensurePythonStarted() explicitly, in the same place they used to inline
 * this logic.
 */
public abstract class BaseActivity extends AppCompatActivity {

    protected void applyPhotoChessChrome() {
        getSupportActionBar().hide();
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            getWindow().setStatusBarColor(getColor(R.color.mycol));
        }
    }

    protected void ensurePythonStarted() {
        if (!Python.isStarted()) {
            Python.start(new AndroidPlatform(this));
        }
    }
}
