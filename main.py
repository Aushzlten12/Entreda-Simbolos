import base64
import glob
import os
import tempfile

import numpy as np
from flask import Flask, redirect, request, send_file
from skimage import io

app = Flask(__name__)

main_html = """
<html>
<head></head>
<script>
  var mousePressed = false;
  var lastX, lastY;
  var ctx;

   function getRndInteger(min, max) {
    return Math.floor(Math.random() * (max - min) ) + min;
   }

  function InitThis() {
      ctx = document.getElementById('myCanvas').getContext("2d");


      numero = getRndInteger(0, 10);
      symbols_name = ["heart","diamond","club","spade"]
      symbols = ["♥", "♦", "♣", "♠"];
      random = Math.floor(Math.random() * symbols.length);
      aleatorio_graf = symbols[random];
      aleatorio = symbols_name[random];

      document.getElementById('mensaje').innerHTML  = 'Dibujando un ' + aleatorio_graf;
      document.getElementById('numero').value = aleatorio;

      $('#myCanvas').mousedown(function (e) {
          mousePressed = true;
          Draw(e.pageX - $(this).offset().left, e.pageY - $(this).offset().top, false);
      });

      $('#myCanvas').mousemove(function (e) {
          if (mousePressed) {
              Draw(e.pageX - $(this).offset().left, e.pageY - $(this).offset().top, true);
          }
      });

      $('#myCanvas').mouseup(function (e) {
          mousePressed = false;
      });
  	    $('#myCanvas').mouseleave(function (e) {
          mousePressed = false;
      });
  }

  function Draw(x, y, isDown) {
      if (isDown) {
          ctx.beginPath();
          ctx.strokeStyle = 'black';
          ctx.lineWidth = 11;
          ctx.lineJoin = "round";
          ctx.moveTo(lastX, lastY);
          ctx.lineTo(x, y);
          ctx.closePath();
          ctx.stroke();
      }
      lastX = x; lastY = y;
  }

  function clearArea() {
      // Use the identity matrix while clearing the canvas
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  }

  //https://www.askingbox.com/tutorial/send-html5-canvas-as-image-to-server
  function prepareImg() {
     var canvas = document.getElementById('myCanvas');
     document.getElementById('myImage').value = canvas.toDataURL();
  }



</script>
<body onload="InitThis();">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js" type="text/javascript"></script>
    <script type="text/javascript" ></script>
    <div align="left">
      <img src="https://upload.wikimedia.org/wikipedia/commons/f/f7/Uni-logo_transparente_granate.png" width="300"/>
    </div>
    <div align="center">
        <h1 id="mensaje">Dibujando...</h1>
        <canvas id="myCanvas" width="200" height="200" style="border:2px solid black"></canvas>
        <br/>
        <br/>
        <button onclick="javascript:clearArea();return false;">Borrar</button>
    </div>
    <div align="center">
      <form method="post" action="upload" onsubmit="javascript:prepareImg();"  enctype="multipart/form-data">
      <input id="numero" name="numero" type="hidden" value="">
      <input id="myImage" name="myImage" type="hidden" value="">
      <input id="bt_upload" type="submit" value="Enviar">
      </form>
    </div>
</body>
</html>
"""


@app.route("/")
def main():
    return main_html


@app.route("/upload", methods=["POST"])
def upload():
    try:
        # check if the post request has the file part
        img_data = request.form.get("myImage").replace("data:image/png;base64,", "")
        aleatorio = request.form.get("numero")
        print("Simbolo: ", aleatorio)
        if not os.path.exists(aleatorio):
            os.makedirs(aleatorio)
        with tempfile.NamedTemporaryFile(
            delete=False, mode="w+b", suffix=".png", dir=aleatorio
        ) as fh:
            fh.write(base64.b64decode(img_data))
        # file = request.files['myImage']
        print("Image uploaded")
    except Exception as err:
        print("Error occurred")
        print(err)

    return redirect("/", code=302)


@app.route("/prepare", methods=["GET"])
def prepare_dataset():
    try:
        images = []
        d = ["♥", "♦", "♣", "♠"]
        simbols_name = ["heart", "diamond", "club", "spade"]
        digits = []
        for i, digit in enumerate(d):
            if not os.path.exists(simbols_name[i]):
                os.makedirs(simbols_name[i])
            filelist = glob.glob(f"{simbols_name[i]}/*.png")
            if filelist:
                images_read = io.concatenate_images(io.imread_collection(filelist))
                images_read = images_read[:, :, :, 3]
                digits_read = np.array([digit] * images_read.shape[0])
                images.append(images_read)
                digits.append(digits_read)
        if images and digits:
            images = np.vstack(images)
            digits = np.concatenate(digits)
            np.save("X.npy", images)
            np.save("y.npy", digits)
        return "OK!"
    except Exception as e:
        print(f"Error in prepare_dataset: {e}")
        return "Error occurred", 500


@app.route("/X.npy", methods=["GET"])
def download_X():
    return send_file("./X.npy")


@app.route("/y.npy", methods=["GET"])
def download_y():
    return send_file("./y.npy")


if __name__ == "__main__":
    symbols = ["heart", "diamond", "club", "spade"]
    for s in symbols:
        if not os.path.exists(s):
            os.mkdir(s)
    app.run()
