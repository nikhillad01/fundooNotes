$(document).ready(function(){
$("#menu-toggle").click(function(e) {
// e.preventDefault();
console.log(e);
$("#wrapper").toggleClass("active");
/* alert(1);*/
});

$("#myModal").on('show.bs.modal', function (e) {

		var title = $('#title').val();
		var description = $('#description').val();
		//Pass Values in modal
		console.log(title)

		$('.modal-body #title').val(title);
		$('.modal-body #description').val(description);
	});
});
