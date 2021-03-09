const btnDelete = document.querySelectorAll('.btn-delete');

if (btnDelete) {
    const btnArray = Array.from(btnDelete);
    btnArray.forEach((btn) => {
        btn.addEventListener('click', (e) => {
            if (!confirm('Are you sure you want to delete it?')) {
                e.preventDefault();
            }
        });
    });
};

const btnCancel = document.querySelectorAll('.btn-cancelar');

if (btnCancel) {
    const btnArray = Array.from(btnCancel);
    btnArray.forEach((btn) => {
        btn.addEventListener('click', (e) => {
            if (!confirm('Va a salir de su registro.\n\n¿Esta usted seguro?')) {
                e.preventDefault();
            }
        });
    });
};

let input = document.getElementById('idCodeColegio');
let checkedColegio = document.getElementById('idCheckColegio');
checkedColegio.onchange = function () {
    if (this.checked == true) {
        input.disabled = false;
        input.focus();
    } else {
        input.disabled = true;
    }
};

let departmentborn_select = document.getElementById('dpDepartBorn');
let provinceborn_select = document.getElementById('dpProvinceBorn');
let districtborn_select = document.getElementById('dpDistrictBorn');

departmentborn_select.onchange = function () {
    value_depart = departmentborn_select.value;
    if (value_depart != 0) {
        fetch('/selectProvince/' + value_depart).then(function (response) {
            response.json().then(function (data) {
                let optionHTML = '<option value="0" selected>Provincia de Nacimiento</option>';
                for (let province of data.provinces) {
                    optionHTML += '<option value="' + province.id + '">' + province.name_province + '</option>';
                }
                provinceborn_select.innerHTML = optionHTML;
            });
        });
    } else {
        cleanSelectProvince("B");
    }
    cleanSelectDistrict("B");
};

provinceborn_select.onchange = function () {
    value_depart = departmentborn_select.value;
    value_province = provinceborn_select.value;
    if (value_province != 0) {
        fetch('/selectDistrict/' + value_province + '/' + value_depart).then(function (response) {
            response.json().then(function (data) {
                let optionHTML = '<option value="0" selected>Distrito de Nacimiento</option>';
                for (let district of data.districts) {
                    optionHTML += '<option value="' + district.id + '">' + district.name_district + '</option>';
                }
                districtborn_select.innerHTML = optionHTML;
            });
        });
    } else {
        cleanSelectDistrict("B");
    }
};

let department_select = document.getElementById('dpDepart');
let province_select = document.getElementById('dpProvince');
let district_select = document.getElementById('dpDistrict');

department_select.onchange = function () {
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
        cleanSelectProvince("O");
    }
    cleanSelectDistrict("O");
};

province_select.onchange = function () {
    value_depart = department_select.value;
    value_province = province_select.value;
    if (value_province != 0) {
        fetch('/selectDistrict/' + value_province + '/' + value_depart).then(function (response) {
            response.json().then(function (data) {
                let optionHTML = '<option value="0" selected>Distrito</option>';
                for (let district of data.districts) {
                    optionHTML += '<option value="' + district.id + '">' + district.name_district + '</option>';
                }
                district_select.innerHTML = optionHTML;
            });
        });
    } else {
        cleanSelectDistrict("O");
    }
};

function cleanSelectProvince(dist) {
    if (dist == "B") {
        provinceborn_select = document.getElementById('dpProvinceBorn');
        provinceborn_select.innerHTML = '<option value="0" selected>Provincia de Nacimiento</option>';
    }
    else {
        province_select = document.getElementById('dpProvince');
        province_select.innerHTML = '<option value="0" selected>Provincia</option>';
    }
};

function cleanSelectDistrict(dist) {
    if (dist == "B") {
        select = document.getElementById('dpDistrictBorn');
        select.innerHTML = '<option value="0" selected>Distrito de Nacimiento</option>';
    }
    else {
        select = document.getElementById('dpDistrict');
        select.innerHTML = '<option value="0" selected>Distrito</option>';
    }
};

let yearborn_select = document.getElementById('dpYearBorn');
let monthborn_select = document.getElementById('dpMonthBorn');
let dayborn_select = document.getElementById('dpDayBorn');

yearborn_select.innerHTML = getYear();

yearborn_select.onchange = function () {
    value_year = yearborn_select.value;
    if (value_year > 0) {
        monthborn_select.innerHTML = getMonth();
    }
    else {
        monthborn_select.innerHTML = '<option value="0" selected>Mes de Nacimiento</option>';
    }
    dayborn_select.innerHTML = '<option value="0" selected>Día de Nacimiento</option>';
};

monthborn_select.onchange = function () {
    value_year = yearborn_select.value;
    value_month = monthborn_select.value;
    if (value_year > 0 && value_month > 0) {
        dayborn_select.innerHTML = getDay(value_year, value_month);
    }
    else {
        dayborn_select.innerHTML = '<option value="0" selected>Día de Nacimiento</option>';
    }
};

function getYear() {
    var yearborn = new Date().getFullYear();
    let optionHTML = '<option value="0" selected>Año de Nacimiento</option>';
    for (var i = yearborn; i >= (yearborn - 65); i--) {
        optionHTML += '<option value="' + i + '">' + i + '</option>';
    }
    return optionHTML;
};

function getMonth() {
    var monthYear = ['Enero', 'Febrero', 'Marzo', 'Abril',
        'Mayo', 'Junio', 'Julio', 'Agosto',
        'Setiembre', 'Octubre', 'Noviembre', 'Diciembre'];
    let optionHTML = '<option value="0" selected>Mes de Nacimiento</option>';
    for (i = 0; i < monthYear.length; i++) {
        optionHTML += '<option value="' + (i + 1) + '">' + monthYear[i] + '</option>';
    }
    return optionHTML;
};

function getDay(year, month) {
    if ((year % 4) == 0) {
        var day = {
            1: 31, 2: 29, 3: 31, 4: 30,
            5: 31, 6: 30, 7: 31, 8: 31,
            9: 30, 10: 31, 11: 30, 12: 31
        };
    }
    else {
        var day = {
            1: 31, 2: 28, 3: 31, 4: 30,
            5: 31, 6: 30, 7: 31, 8: 31,
            9: 30, 10: 31, 11: 30, 12: 31
        };
    }
    let optionHTML = '<option value="0" selected>Día de Nacimiento</option>';
    for (i = 0; i < day[month]; i++) {
        optionHTML += '<option value="' + (i + 1) + '">' + (i + 1) + '</option>';
    }
    return optionHTML;
};