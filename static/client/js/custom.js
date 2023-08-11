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
