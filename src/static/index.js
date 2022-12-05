const add_model_show = document.getElementById("add_model");


add_model_show.onclick = function () {
     let title = document.getElementById("modal_label");
     title.innerText = "Создать модель";
     $('#modal').modal('show');
}

function show_error(message) {
    let title = document.getElementById("modal_label");
    title.innerText = "Ошибка";
    let text_area = document.getElementById("modal_body");
    text_area.innerText = message;
    $('#modal').modal('show');
}
function show_fit_model(id) {
    let title = document.getElementById("modal_label");
    title.innerText = "Обучить модель";
    $('#modal').modal('show');
}

function show_predict_with_model(id) {
    let title = document.getElementById("modal_label");
    title.innerText = "Предсказать результаты";
    $('#modal').modal('show');
}
function get_info_about_model(id) {
    let title = document.getElementById("modal_label");
    title.innerText = "Информация о модели";
    $('#modal').modal('show');
}
function create_table(data_dict) {
    let data = [];
    for (let d in data_dict){
        data.push([d, data_dict[d]])
    }
    let table = document.getElementById('tbl');
     table.innerHTML = `
        <thead>
        <tr class="table_header">
            <th>Название модели</th>
            <th>Тип модели</th>
            <th>Описание</th>
            <th>Параметры и информация</th>
            <th>Действия</th>
        </tr>
        </thead>
        <tbody>
    `;
     for (let j = 0; j < data.length; ++j) {
         table.innerHTML += `
         <tr class="table_row">
            <td>${data[j][1]}</td>
            <td>${data[j][2]}</td>
            <td>${data[j][3]}</td>
            <td><button class="btn btn-primary" onclick="get_info_about_model('${data[j][0]}')">Подробнее</button></td>
            <td>
                <button class="btn btn-warning" onclick="show_fit_model('${data[j][0]}')">Обучить</button>
                <button class="btn btn-success" onclick="show_predict_with_model('${data[j][0]}')">Предсказать</button>
                <button class="btn btn-danger" onclick="delete_model('${data[j][0]}')">Удалить</button>
            </td>
         </tr>
        `;
     }
     table.innerHTML += '</tbody>';
}

function delete_model(id) {
    get_all_models();
}
function get_all_models() {
    axios.get('/get_all_models')
        .then(response => {
            result = response.data;
            create_table(result);
        });
}

window.onload = function () {
    get_all_models();
}
