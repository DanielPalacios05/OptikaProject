function confirmUpload(input,url) {

    modalRef = document.getElementById('modal-delete')

    var myModal = new bootstrap.Modal(modalRef)

    modalRef.addEventListener('hidden.bs.modal', function (event) {
        modalRef.parentNode.getElementsByClassName("form-control pictureInput")[0].value="";
    });

    myModal.toggle()
}

function readURL(input) {
    if (input.files && input.files[0]) {
      var reader = new FileReader();
      reader.onload = function (e) {
        $('#blah')
          .attr('src', e.target.result)
          .width(150)
          .height(200);
      };
      reader.readAsDataURL(input.files[0]);
    }
  }