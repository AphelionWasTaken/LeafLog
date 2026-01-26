package org.test.leaflog;

import android.app.Activity;
import android.content.Intent;
import android.webkit.WebChromeClient;
import android.webkit.ValueCallback;
import android.webkit.WebView;
import java.util.List;
import android.net.Uri;
import android.provider.MediaStore;
import android.content.pm.PackageManager;
import android.os.Environment;
import java.io.File;
import java.io.IOException;
import androidx.core.content.FileProvider;


public class LeafLogChromeClient extends WebChromeClient {
    public static ValueCallback<android.net.Uri[]> fileCallback;
    public static Uri cameraImageUri;
    private Activity activity;
    private static final int FILE_PICKER_CODE = 1001;


    public LeafLogChromeClient(Activity activity) {
        this.activity = activity;
    }


    @Override
    public boolean onShowFileChooser(
        WebView webView,
        ValueCallback<android.net.Uri[]> filePathCallback,
        FileChooserParams fileChooserParams
    ) {
        cameraImageUri = null;
        fileCallback = filePathCallback;

        Intent galleryIntent = new Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
        galleryIntent.setType("image/*");
        galleryIntent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true);
        galleryIntent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        Intent cameraIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        try {
            File photoFile = createImageFile();    
            String authority = activity.getPackageName() + ".fileprovider";             
            cameraImageUri = FileProvider.getUriForFile(
                activity,
                authority,
                photoFile
            );
            
            cameraIntent.putExtra(MediaStore.EXTRA_OUTPUT, cameraImageUri);
            cameraIntent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION);

            List resolveList = activity.getPackageManager().queryIntentActivities(cameraIntent, PackageManager.MATCH_DEFAULT_ONLY);
            for (Object obj : resolveList) {
                android.content.pm.ResolveInfo ri = (android.content.pm.ResolveInfo) obj;
                activity.grantUriPermission(ri.activityInfo.packageName, cameraImageUri, Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
            }
        } catch (IOException e) {
            e.printStackTrace();
            cameraIntent = null;
        }

        Intent chooser = Intent.createChooser(galleryIntent, "Select source");
        if (cameraIntent != null) {
            chooser.putExtra(Intent.EXTRA_INITIAL_INTENTS, new Intent[]{cameraIntent});
        }

        chooser.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
        activity.startActivityForResult(chooser, FILE_PICKER_CODE);
        return true;
    }


    public void sendUrisToCallback(List<Uri> uris) {
        if (fileCallback != null) {
            Uri[] array = uris.toArray(new Uri[0]);
            fileCallback.onReceiveValue(array);
            fileCallback = null;
        }
    }


    public Uri getCameraImageUri() {
        return cameraImageUri;
    }


    private File createImageFile() throws IOException {
        String fileName = "IMG_" + System.currentTimeMillis();
        File storageDir = activity.getExternalFilesDir(Environment.DIRECTORY_PICTURES);
        if (storageDir != null && !storageDir.exists()) {
            storageDir.mkdirs();
        }

        return File.createTempFile(fileName, ".jpg", storageDir);
    }
}