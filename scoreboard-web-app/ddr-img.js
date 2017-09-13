$(document).ready(function () {
      // This will update the score every 2 sec (2000 millisec)
      //setInterval(updateScore, 2000);
      setInterval(updateImage, 4000);
    })

    function updateImage() {
      $.ajax({
        type: 'GET',
        url: 'API_URL_TOKEN/image?lek=' + getUrlParam(),
        contentType: 'application/json',
        dataType: 'json',
        success: function(response){
          if(response) {
              if (response.code == 'FAIL') {
                $('#gg1').text("Internal server error!");
              } else {
                image_name = response.image;
                lek = response.lastEvaluatedKey;
                console.log(image_name);
                encodedLek = encodeURIComponent(JSON.stringify(lek))
                console.log("Decoded lek: " + decodeURIComponent(encodedLek));

                if (image_name) {
                  image_url = "https://s3-us-west-2.amazonaws.com/S3_BUCKET_TOKEN/" + image_name;
//                  var image_tag = document.getElementById('danceImage');
//                  var downloadingImage = new Image();
//                  downloadingImage.onload = function(){
//                    image_tag.src = this.src;
//                  };
//                  downloadingImage.src = image_url;

                  var image_link = document.getElementById('ddrLink');

                  image_link.href = image_url;
                  image_link.style = "background-image: url(" + image_url + "); transform-origin: right bottom 0px;";

                }

                var imageCaption = document.getElementById('ddrCaption');
                imageCaption.innerHTML = getDanceCaption();

                var graphics_link = document.getElementById('graphicsLink');
                var imageIndex = Math.floor((Math.random() * 16) + 1);
                var graphicsUrl = "img/" + imageIndex + ".jpg";
                graphics_link.href = graphicsUrl;
                graphics_link.style = "background-image: url(" + graphicsUrl + "); transform-origin: right bottom 0px;";

                var imageCaption = document.getElementById('graphicsCaption');
                imageCaption.innerHTML = getDanceCaption();

                var lekDiv = document.getElementById('lekDiv');
                if(lek) {
                lekDiv.innerHTML = encodeURIComponent(JSON.stringify(lek));
                }
              }
          }
        },
        error: function(e) {
          if(e) {
            $('#gg1').text(e);
          }
        }
      })
    }

    function getUrlParam() {
      var lekDiv = document.getElementById('lekDiv');
      var lek = lekDiv.innerHTML;
      if (lek) {
        return lek;
      } else {
        return "null";
      }
    }

    function getDanceCaption() {
        var danceWords = [
            "Outstanding",
            "Love It!",
            "Nice!",
            "Mind blowing",
            "You can do it!",
            "Lets go!",
            "W00t W00t",
            "Woo hoo",
            "Hip Hip Hop Hop",
            "Boom",
            "YAY!!!",
            "Awesome",
            "Once more",
            "Encore",
            "Go Vegas"
        ]
        var x = Math.floor((Math.random() * danceWords.length));
        return danceWords[x];
    }
