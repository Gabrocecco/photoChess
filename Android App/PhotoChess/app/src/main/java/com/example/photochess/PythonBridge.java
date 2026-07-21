package com.example.photochess;

import android.content.Context;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

/**
 * Thin wrapper around the Chaquopy "android_api" module lookup (see
 * android_api.py under app/src/main/python/), factored out of what used to
 * be duplicated in CameraActivity and AnalyzeActivity.
 *
 * callAttr() is a pure passthrough returning the raw PyObject, same as
 * calling module.callAttr(...) directly used to — callers still do their
 * own .toString(), .equals("Error"), and .toJava(...) exactly as before.
 * This only consolidates *how a module handle is obtained*, not any of the
 * result parsing/error-handling logic, to keep the change mechanical and
 * reviewable without a compiler (no Gradle/Android SDK available in the
 * environment this was written in — see CLAUDE.md's Fase 3 caveat).
 */
public class PythonBridge {
    private final PyObject module;

    public PythonBridge(Context context) {
        if (!Python.isStarted()) {
            Python.start(new AndroidPlatform(context));
        }
        module = Python.getInstance().getModule("android_api");
    }

    public PyObject callAttr(String name, Object... args) {
        return module.callAttr(name, args);
    }
}
