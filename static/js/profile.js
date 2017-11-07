function handleFileSelect(evt) {
    var files = evt.target.files; // FileList object

    // use the 1st file from the list
    f = files[0];

    var reader = new FileReader();

    // Closure to capture the file information.
    reader.onload = (function(theFile) {
        return function(e) {
            document.getElementById('image-preview').src = e.target.result
        };
      })(f);

      // Read in the image file as a data URL.
      reader.readAsText(f);
  };

document.getElementById('file-upload').addEventListener('change', handleFileSelect, false);
