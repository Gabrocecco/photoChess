package com.example.photochess;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;

import android.content.DialogInterface;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.drawable.PictureDrawable;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;

import com.caverock.androidsvg.SVG;
import com.caverock.androidsvg.SVGParseException;
import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

import java.io.File;

public class AnalyzeActivity extends AppCompatActivity {

    ImageView nextMoveBtn;
    String fen = "";
    PyObject module;
    ImageView boardPhoto;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_analyze);

        getSupportActionBar().hide();

        if(Build.VERSION.SDK_INT >= Build.VERSION_CODES.M)
        {
            getWindow().setStatusBarColor(getColor(R.color.mycol));
        }

        Intent intent = getIntent();
        fen = intent.getExtras().getString("fen");

        nextMoveBtn = findViewById(R.id.bmoveBtn);
        if (! Python.isStarted()) {
            Python.start(new AndroidPlatform(this));
        }
        Python py = Python.getInstance();
        module = py.getModule("getbestmove");
        PyObject el = module.callAttr("getboard", fen);

        boardPhoto = findViewById(R.id.boardView);
        PictureDrawable drawable = getPictureDrawablefromSvg(el.toString());
        boardPhoto.setImageDrawable(drawable);
        nextMoveBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                getBestMove();
            }
        });


    }

    public void getBestMove(){
        PyObject response = module.callAttr("getbestmove", fen);
        PyObject movedSvg = module.callAttr("getmoveboard", fen, response.toString().substring(0,2), response.toString().substring(2,4));

        PictureDrawable drawable = getPictureDrawablefromSvg(movedSvg.toString());

        boardPhoto.setImageDrawable(drawable);
    }


    public PictureDrawable getPictureDrawablefromSvg(String svgString){
        SVG svg = null;
        try {
            svg = SVG.getFromString(svgString);
        } catch (SVGParseException e) {
            throw new RuntimeException(e);
        };
        PictureDrawable drawable = new PictureDrawable(svg.renderToPicture());
        return drawable;
    }

}