package com.example.photochess;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;

import android.content.DialogInterface;
import android.content.Intent;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
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

        ImageView howBtn = findViewById(R.id.howButton);
        howBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                howtotakephoto();
            }
        });

    }

    public void howtotakephoto(){
       View howlayout = getLayoutInflater().inflate(R.layout.how_dialog, null, false);
       AlertDialog.Builder builder = new AlertDialog.Builder(this);
       builder.setView(howlayout);
       builder.setTitle("How to take the photo");
       builder.setIcon(R.drawable.blackrook);
       builder.setPositiveButton("Close", new DialogInterface.OnClickListener() {
           public void onClick(DialogInterface dialog, int which) {
           }});
       AlertDialog alert = builder.create();
       alert.show();
       alert.getButton(DialogInterface.BUTTON_POSITIVE).setTextColor(getResources().getColor(R.color.mygreen));
    }

}