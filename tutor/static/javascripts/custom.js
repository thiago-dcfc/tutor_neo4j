$('#messages-box').delay(3000).fadeOut(400);

// Example starter JavaScript for disabling form submissions if there are invalid fields
(function () {
    'use strict'

    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    var forms = document.querySelectorAll('.needs-validation')

    // Loop over them and prevent submission
    Array.prototype.slice.call(forms)
        .forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (!form.checkValidity()) {
                event.preventDefault()
                event.stopPropagation()
                }

                form.classList.add('was-validated')
            }, false)
        })
})()

$('.delete-course-class').click(function(){
    return confirm("Tem certeza que deseja excluir a disciplina?");
})

$('.delete-class-subject').click(function(){
    return confirm("Tem certeza que deseja excluir o assunto?");
})

$('.delete-question').click(function(){
    return confirm("Tem certeza que deseja excluir a questão?");
})

// ClassicEditor
//         .create( document.querySelector( '.editor' ) )
//         .catch( error => {
//             console.error( error );
//         } );