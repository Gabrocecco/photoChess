package com.example.photochess;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;

import android.content.Intent;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        getSupportActionBar().hide();


        if(Build.VERSION.SDK_INT >= Build.VERSION_CODES.M)
        {
            getWindow().setStatusBarColor(getColor(R.color.mycol));
        }

        if (! Python.isStarted()) {
            Python.start(new AndroidPlatform(this));
        }

        ImageView btn = (ImageView) findViewById(R.id.photoButton);

        btn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startActivity(new Intent(MainActivity.this, CameraActivity.class));
            }
        });

    }

}