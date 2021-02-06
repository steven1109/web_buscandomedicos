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
        cleanSelectProvince();
    }
    cleanSelectDistrict();
};

province_select.onchange = function () {
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
};

function cleanSelectProvince() {
    province_select = document.getElementById('dpProvince');
    province_select.innerHTML = '<option value="0" selected>Provincia</option>';
};

function cleanSelectDistrict() {
    select = document.getElementById('dpDistrict');
    select.innerHTML = '<option value="0" selected>Distrito</option>';
};

const search = document.getElementById('searchEspecialidad');
const matchlist = document.getElementById('match-list');

const searchStates = async searchText => {
    const res = await fetch('/allEspecialidades');
    const states = await res.json();

    let matches = states.especialidades.filter(state => {
        const regex = new RegExp(`^${searchText}`, 'gi');
        return state.name_especialidad.match(regex);
    });

    if (searchText.length === 0){
        matches = [];
        matchlist.innerHTML = '';
    }

    outputHtml(matches);
}

const outputHtml = matches => {
    if(matches.length > 0){
        let html = ``;
        for (es of matches) {
            html += `
                <div class="card card-body mb-1">
                    <h6>${es.name_especialidad}</h6>
                </div>
            `;
        }

        matchlist.innerHTML = html;
    }
}

search.addEventListener('input', () => searchStates(search.value));

function filterValuePart(arr, part) {
    return arr.filter(function (obj) {
        return Object.keys(obj)
            .some(function (k) {
                return obj[k].indexOf(part) !== -1;
            });
    });
};