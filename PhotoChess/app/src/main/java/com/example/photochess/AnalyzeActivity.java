package com.example.photochess;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;

import android.content.DialogInterface;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;

import java.io.File;

public class AnalyzeActivity extends AppCompatActivity {

    Button nextMoveBtn;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_analyze);

        getSupportActionBar().hide();

        if(Build.VERSION.SDK_INT >= Build.VERSION_CODES.M)
        {
            getWindow().setStatusBarColor(getColor(R.color.mycol));
        }

        nextMoveBtn = findViewById(R.id.bmoveBtn);
        ImageView boardPhoto = findViewById(R.id.boardView);

        File file = new File(getFilesDir(), "boardPhoto");
        Bitmap bitmap = BitmapFactory.decodeFile(file.getPath());
        boardPhoto.setImageResource(R.drawable.chessboard);
        nextMoveBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                getBestMove();
            }
        });


    }

    public void getBestMove(){
        ImageView alertView = new ImageView(this);
        alertView.setImageResource(R.drawable.ic_launcher_background);
        new AlertDialog.Builder(this)
                .setTitle("Your best next move:")
                .setMessage("Move Tower to A4")
                .setView(alertView)
                // Specifying a listener allows you to take an action before dismissing the dialog.
                // The dialog is automatically dismissed when a dialog button is clicked.
                .setPositiveButtonIcon((getDrawable(R.drawable.usebtn)))

                // A null listener allows the button to dismiss the dialog and take no further action.
                .setIcon(R.drawable.towerlogo)
                .show();
    }

}