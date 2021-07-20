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

function createDeletePrompt(element, text) {
    $(element).click(function () {
        return confirm("Tem certeza que deseja excluir " + text + "?");
    })
}

function createCKEditor(element) {
    CKEDITOR.replace(element, {
        extraPlugins: 'mathjax',
        mathJaxLib: '//cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-AMS_HTML',
        height: 120
    });
}