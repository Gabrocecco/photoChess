package com.example.photochess;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.camera.core.CameraSelector;
import androidx.camera.core.ImageAnalysis;
import androidx.camera.core.ImageCapture;
import androidx.camera.core.ImageProxy;
import androidx.camera.core.Preview;
import androidx.camera.lifecycle.ProcessCameraProvider;
import androidx.camera.view.PreviewView;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import android.Manifest;
import android.content.ContentValues;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.ColorMatrix;
import android.graphics.ColorMatrixColorFilter;
import android.graphics.Paint;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.Toast;

import com.google.common.util.concurrent.ListenableFuture;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.UUID;
import java.util.concurrent.Executor;

public class CameraActivity extends AppCompatActivity implements View.OnClickListener{
    private ListenableFuture<ProcessCameraProvider> provider;

    private static final int PERMISSION_REQUEST_CODE = 200;

    private ImageView photoBtn;
    private ImageView useBtn;
    private ImageView undoBtn;
    private PreviewView previewView;
    private ImageView imageView;
    private ImageCapture imageCapt;
    private ImageAnalysis imageAn;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_camera);
        getSupportActionBar().hide();

        if(Build.VERSION.SDK_INT >= Build.VERSION_CODES.M)
        {
            getWindow().setStatusBarColor(getColor(R.color.mycol));
        }

        if (! checkPermission())
            requestPermission();

        photoBtn = findViewById(R.id.photoBtn);
        useBtn = findViewById(R.id.useBtn);
        undoBtn = findViewById(R.id.undoBtn);
        previewView = findViewById(R.id.previewView);
        imageView = findViewById(R.id.imageView);

        photoBtn.setOnClickListener(this);
        useBtn.setOnClickListener(this);
        //this.analysis_on = false;
        undoBtn.setOnClickListener(this);
        undoBtn.setVisibility(View.INVISIBLE);
        useBtn.setVisibility(View.INVISIBLE);
        provider = ProcessCameraProvider.getInstance(this);
        provider.addListener( () ->
        {
            try{
                ProcessCameraProvider cameraProvider = provider.get();
                startCamera(cameraProvider);
            } catch (Exception e)
            {
                e.printStackTrace();
            }
        }, getExecutor());
    }

    private boolean checkPermission() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
                != PackageManager.PERMISSION_GRANTED) {
            // Permission is not granted
            return false;
        }
        return true;
    }

    private void requestPermission() {

        ActivityCompat.requestPermissions(this,
                new String[]{Manifest.permission.CAMERA},
                PERMISSION_REQUEST_CODE);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String permissions[], int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        switch (requestCode) {
            case PERMISSION_REQUEST_CODE:
                if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    Toast.makeText(getApplicationContext(), "Permission Granted", Toast.LENGTH_SHORT).show();

                    // main logic
                } else {
                    Toast.makeText(getApplicationContext(), "Permission Denied", Toast.LENGTH_SHORT).show();
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
                                != PackageManager.PERMISSION_GRANTED) {
                            showMessageOKCancel("You need to allow access permissions",
                                    new DialogInterface.OnClickListener() {
                                        @Override
                                        public void onClick(DialogInterface dialog, int which) {
                                            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                                                requestPermission();
                                            }
                                        }
                                    });
                        }
                    }
                }
                break;
        }
    }

    private void showMessageOKCancel(String message, DialogInterface.OnClickListener okListener) {
        new AlertDialog.Builder(CameraActivity.this)
                .setMessage(message)
                .setPositiveButton("OK", okListener)
                .setNegativeButton("Cancel", null)
                .create()
                .show();
    }

    private void startCamera(ProcessCameraProvider cameraProvider) {
        cameraProvider.unbindAll();
        CameraSelector camSelector = new CameraSelector.Builder().requireLensFacing(CameraSelector.LENS_FACING_BACK).build();

        Preview preview = new Preview.Builder().build();
        preview.setSurfaceProvider(previewView.getSurfaceProvider());

        imageCapt = new ImageCapture.Builder().setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY).build();
        imageAn = new ImageAnalysis.Builder().setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST).build();
        //imageAn.setAnalyzer(getExecutor(), this);

        cameraProvider.bindToLifecycle(this, camSelector, preview, imageCapt, imageAn);
    }

    private Executor getExecutor() {
        return ContextCompat.getMainExecutor(this);
    }

    @Override
    public void onClick(View view)
    {
        switch (view.getId())
        {
            case R.id.photoBtn:
                Log.e("Case", "case");
                capturePhoto();
                break;

            /*case R.id.analysis_bt:
                this.analysis_on = !this.analysis_on;
                break;*/
            case R.id.undoBtn:
                undoPhoto();
                break;
            case R.id.useBtn:
               usePhoto();
               break;

        }
    }

    public void undoPhoto(){
        imageView.setVisibility(View.INVISIBLE);
        previewView.setVisibility(View.VISIBLE);
        photoBtn.setVisibility(View.VISIBLE);
        undoBtn.setVisibility(View.INVISIBLE);
        useBtn.setVisibility(View.INVISIBLE);
    }
    public void capturePhoto() {
        Bitmap bitmapImage = previewView.getBitmap();
        imageView.setVisibility(View.VISIBLE);
        previewView.setVisibility(View.INVISIBLE);
        imageView.setImageBitmap(bitmapImage);
        photoBtn.setVisibility(View.INVISIBLE);
        undoBtn.setVisibility(View.VISIBLE);
        useBtn.setVisibility(View.VISIBLE);
    }

    public void usePhoto(){

        savePhoto(previewView.getBitmap());
        startActivity(new Intent(CameraActivity.this, AnalyzeActivity.class));

    }

    public void savePhoto(Bitmap image){

        try {
            File newfile = new File(getFilesDir(), "boardPhoto");
            if (!newfile.exists()) {
                newfile.createNewFile();
                FileOutputStream out = new FileOutputStream(newfile);
                image.compress(Bitmap.CompressFormat.PNG, 100, out);
                out.flush();
                out.close();
            }
        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
    }

    /*@Override
    public void analyze(@NonNull ImageProxy image) {
        if(this.analysis_on)
        {
            Bitmap conv = pview.getBitmap();
            // Do something here!!!
            conv = toGrayscale(conv);
            this.imview.setImageBitmap( conv );
        }
        image.close();

    }

    public Bitmap toGrayscale(Bitmap bmpOriginal)
    {
        int width, height;
        height = bmpOriginal.getHeight();
        width = bmpOriginal.getWidth();

        Bitmap bmpGrayscale = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888);
        Canvas c = new Canvas(bmpGrayscale);
        Paint paint = new Paint();
        ColorMatrix cm = new ColorMatrix();
        cm.setSaturation(0);
        ColorMatrixColorFilter f = new ColorMatrixColorFilter(cm);
        paint.setColorFilter(f);
        c.drawBitmap(bmpOriginal, 0, 0, paint);
        return bmpGrayscale;
    }*/
}