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
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.RadioButton;
import android.widget.Spinner;
import android.widget.TextView;

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
    View customLayout;
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

        ImageView editChessboardButton = findViewById(R.id.eChessboardBtn);
        editChessboardButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                editChessboard();
            }
        });

        customLayout = getLayoutInflater().inflate(R.layout.edit_dialog, null);
        Spinner columnSpinner = customLayout.findViewById(R.id.column_spinner);
        Spinner lineSpinner = customLayout.findViewById(R.id.line_spinner);
        Spinner pieceSpinner = customLayout.findViewById(R.id.piece_spinner);
        ArrayAdapter<CharSequence> columnAdapter = ArrayAdapter.createFromResource(this, R.array.columns_array, android.R.layout.simple_spinner_item);
        ArrayAdapter<CharSequence> lineAdapter = ArrayAdapter.createFromResource(this, R.array.line_array, android.R.layout.simple_spinner_item);
        ArrayAdapter<CharSequence> pieceAdapter = ArrayAdapter.createFromResource(this, R.array.pieces_array, android.R.layout.simple_spinner_item);

        columnAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        lineAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        pieceAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);

        columnSpinner.setAdapter(columnAdapter);
        lineSpinner.setAdapter(lineAdapter);
        pieceSpinner.setAdapter(pieceAdapter);

        Button addBtn = customLayout.findViewById(R.id.addBtn);
        addBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                addEditString(columnSpinner, lineSpinner, pieceSpinner);
            }
        });

    }

    public void getBestMove(){
        PyObject response = module.callAttr("getbestmove", fen);
        PyObject movedSvg = module.callAttr("getmoveboard", fen, response.toString().substring(0,2), response.toString().substring(2,4));

        PictureDrawable drawable = getPictureDrawablefromSvg(movedSvg.toString());

        boardPhoto.setImageDrawable(drawable);
    }


    public void addEditString(Spinner columnSpinner, Spinner lineSpinner, Spinner pieceSpinner){
        TextView changesText = customLayout.findViewById(R.id.changesTextBox);
        String text = changesText.getText().toString();

        String column = columnSpinner.getSelectedItem().toString();
        String line = lineSpinner.getSelectedItem().toString();
        String piece = pieceSpinner.getSelectedItem().toString();

        if(text.length() > 0)
        {
            text = text + ";" + column + line + ":" + piece;
        }
        else{
            text = column + line + ":" + piece;
        }

        changesText.setText(text);
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

    public void editChessboard(){

        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("Edit chessboard");
        builder.setView(customLayout);
        builder.setIcon(R.drawable.blackrook);
        builder.setPositiveButton("Confirm edit", new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int which) {
                TextView changesText = customLayout.findViewById(R.id.changesTextBox);
                String text = changesText.getText().toString();
                PyObject newFen = module.callAttr("editchessboard", text);
            }
        });

        // A null listener allows the button to dismiss the dialog and take no further action.
        builder.setNegativeButton(android.R.string.no, null);
        AlertDialog alert = builder.create();
        alert.show();
        alert.getButton(DialogInterface.BUTTON_POSITIVE).setTextColor(getResources().getColor(R.color.mygreen));
        alert.getButton(DialogInterface.BUTTON_NEGATIVE).setTextColor(getResources().getColor(R.color.mycol));
    }

}