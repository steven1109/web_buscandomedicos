const btnDelete = document.querySelectorAll('.btn-delete')

if (btnDelete) {
    const btnArray = Array.from(btnDelete);
    btnArray.forEach((btn) => {
        btn.addEventListener('click', (e) => {
            if (!confirm('Are you sure you want to delete it?')) {
                e.preventDefault();
            }
        });
    });
}

// let state_select = document.getElementById('dpDepart');
// state_select.onchange = function() {
//     state = state_select.nodeValue;
//     console.log(state);
// };
$('#dpDepart').change(function () {
    let department_select = document.getElementById('dpDepart');
    let province_select = document.getElementById('dpProvince');

    value_depart = department_select.value;
    if (value_depart != 0) {
        fetch('/selectProvince/' + value_depart).then(function (response) {

            response.json().then(function (data) {
                let optionHTML = '<option value="0" selected>Provincia</option>';
                for (let province of data.provinces) {
                    optionHTML += '<option value="' + province.id + '">' + province.name_province + '</option>';
                }
                province_select.innerHTML = optionHTML;
            });
        });
    } else {
        cleanSelectProvince();
    }
})

$('#dpProvince').change(function () {
    let province_select = document.getElementById('dpProvince');
    let district_select = document.getElementById('dpDistrict')

    value_province = province_select.value;
    if (value_province != 0) {
        fetch('/selectDistrict/' + value_province).then(function (response) {
            response.json().then(function (data) {
                let optionHTML = '<option value="0" selected>Distrito</option>';
                for (let district of data.districts) {
                    optionHTML += '<option value="' + district.id + '">' + district.name_district + '</option>';
                }
                district_select.innerHTML = optionHTML;
            });
        });
    } else {
        cleanSelectDistrict();
    }
})

function cleanSelectProvince() {
    province_select = document.getElementById('dpProvince');
    // if(province_select.length > 0){
    //     var options = document.querySelectorAll('#dpProvince option');
    //     options.forEach(o => o.remove());
    // }
    let optionHTML = '<option value="0" selected>Provincia</option>';
    province_select.innerHTML = optionHTML;
}

function cleanSelectDistrict() {
    select = document.getElementById('dpDistrict');
    select.innerHTML = '<option value="0" selected>Distrito</option>';
}
