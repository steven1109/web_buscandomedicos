const btnDelete = document.querySelectorAll('.btn-delete')

if(btnDelete){
    const btnArray = Array.from(btnDelete);
    btnArray.forEach((btn) => {
        btn.addEventListener('click', (e) => {
            if(!confirm('Are you sure you want to delete it?')){
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
$('#dpDepart').change(function(){ 
    let state_select = document.getElementById('dpDepart');
    // if (this.selectedIndex !== 0) {
    //     console.log(this.value);
    // }
    console.log(state_select.value);
 })
