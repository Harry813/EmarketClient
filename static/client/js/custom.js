const notyf = new Notyf({
    duration: 2000,
    position: {
        x: 'right',
        y: 'top',
    },
    types: [
        {
            type: 'success',
            background: '#00c853',
            dismissible: true,
            icon: {
                className: 'fas fa-check',
                tagName: 'i',
                text: '',
                color: '#fff',
            },
        }, {
            type: 'error',
            duration: 3000,
            dismissible: true,
            background: '#d50000',
            icon: {
                className: 'fas fa-xmark',
                tagName: 'i',
                text: '',
                color: '#fff',
            },
        }, {
            type: 'info',
            background: '#2962ff',
            icon: {
                className: 'fas fa-info',
                tagName: 'i',
                text: '',
                color: '#fff',
            },
        }, {
            type: 'warning',
            duration: 2500,
            dismissible: true,
            background: '#ff6d00',
            icon: {
                className: 'fas fa-exclamation',
                tagName: 'i',
                text: '',
                color: '#fff',
            },
        }
    ]
});

$(document).on('click', 'a.add_wishlist, button.add_wishlist', function (e) {
    e.preventDefault();
    let $this = $(this);
    let variant_id = $this.data('variant');

    $.ajax({
        url: kern_wishlist,
        type: 'POST',
        data: {
            id: variant_id,
        },
        headers: {
            'X-CSRFToken': csrfToken
        },
        success: function (data) {
            notyf.success(data["msg"]);
        },
        error: function (data) {
            if (data.responseJSON["detail"] === "Authentication credentials were not provided.") {
                notyf.error('{% trans "用户尚未登录，无法使用该功能" %}');
            } else {
                notyf.error(data["msg"]);
            }
        }
    });
});

$(document).on('click', 'a.remove_wishlist, button.remove_wishlist', function (e) {
    e.preventDefault();
    let $this = $(this);
    let variant_id = $this.data('variant');

    $.ajax({
        url: kern_wishlist + "?id=" + variant_id,
        type: 'DELETE',
        data: {
            id: variant_id,
        },
        headers: {
            'X-CSRFToken': csrfToken
        },
        success: function (data) {
            console.log(data);
            notyf.success(data["msg"]);
            setTimeout(function () {
                window.location.reload();
            }, 1500);
        },
        error: function (data) {
            if (data.responseJSON["detail"] === "Authentication credentials were not provided.") {
                notyf.error('{% trans "用户尚未登录，无法使用该功能" %}');
            } else {
                notyf.error(data["msg"]);
            }
        }
    });
});

$(document).on('click', 'a.add_cart, button.add_cart', function (e) {
    e.preventDefault();
    let $this = $(this);
    let variant_id = $this.data('variant');

    $.ajax({
        url: kern_cart,
        type: 'POST',
        data: {
            id: variant_id,
        },
        headers: {
            'X-CSRFToken': csrfToken
        },
        success: function (data) {
            notyf.success(data["msg"]);
        },
        error: function (data) {
            console.log(data)
            if (data.responseJSON["detail"] === "Authentication credentials were not provided.") {
                notyf.error('{% trans "用户尚未登录，无法使用该功能" %}');
            } else {
                notyf.error(data["msg"]);
            }
        }
    });
});

$(document).on('click', 'a.remove_cart, button.remove_cart', function (e) {
    e.preventDefault();
    let $this = $(this);
    let variant_id = $this.data('variant');

    $.ajax({
        url: kern_cart + "?id=" + variant_id,
        type: 'DELETE',
        headers: {
            'X-CSRFToken': csrfToken
        },
        success: function (data) {
            console.log(data);
            notyf.success(data["msg"]);
            setTimeout(function () {
                window.location.reload();
            }, 1500);
        },
        error: function (data) {
            console.log(data)
            if (data.responseJSON["detail"] === "Authentication credentials were not provided.") {
                notyf.error('{% trans "用户尚未登录，无法使用该功能" %}');
            } else {
                notyf.error(data["msg"]);
            }
        }
    });
});

$(document).on('submit', 'form.add_cart_form', function (e) {
    e.preventDefault();
    let $this = $(this);
    let $quantity = $this.find('input[name="quantity"]');
    let variant_id = $quantity.data('variant');
    $.ajax({
        url: kern_cart,
        type: 'POST',
        data: {
            id: variant_id,
            quantity: $quantity,
        },
        headers: {
            'X-CSRFToken': csrfToken
        },
        success: function (data) {
            notyf.success(data["msg"]);
        },
        error: function (data) {
            if (data.responseJSON["detail"] === "Authentication credentials were not provided.") {
                notyf.error('{% trans "用户尚未登录，无法使用该功能" %}');
            } else {
                notyf.error(data["msg"]);
            }
        }
    });
});