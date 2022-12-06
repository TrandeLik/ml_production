const add_model_show = document.getElementById("add_model");


add_model_show.onclick = function () {
     let title = document.getElementById("modal_label");
     title.innerText = "Создать модель";
     let form = document.getElementById("modal_body");
     form.innerHTML = `
        <div class="form-group">
            <label for="model_type">Тип модели</label>
            <select class="form-select form-control" id="model_type">
                <option value="bt">Бустинг</option>
                <option value="rf">Случайный лес</option>
            </select>
            <label for="model_name" style="margin-top: 1rem">Название модели</label>
            <input type="text" class="form-control" id="model_name">
            <label for="model_descr" style="margin-top: 1rem">Описание модели</label>
            <textarea type="text" class="form-control" id="model_descr"></textarea>
            <label for="model_estimators" style="margin-top: 1rem">Количество деревьев</label>
            <small class="form-text text-muted">Ничего не вводите для 100 деревьев</small>
            <input type="number" class="form-control" id="model_estimators" min="1">
            <label for="model_depth" style="margin-top: 1rem">Глубина деревьев</label>
            <input type="number" class="form-control" id="model_depth" min="1">
            <small class="form-text text-muted">Ничего не вводите для неограниченной глубины</small>
            <label for="model_features" style="margin-top: 1rem">Размер признакового пространства для каждого дерева</label>
            <input type="number" class="form-control" id="model_features" min="0" max="1" step="0.01">
            <small class="form-text text-muted">Ничего не вводите для значения равного 1/3</small>
            <label for="model_lr" style="margin-top: 1rem">Learning rate</label>
            <input type="number" class="form-control" id="model_lr" min="0" step="0.01">
            <small class="form-text text-muted">Нужно заполнить только для градиентного бустинга. Ничего не вводите для значения 0.1</small>
        </div>
     `;
     let footer = document.getElementById("modal_footer");
     footer.innerHTML = `
       <button type="button" class="btn btn-success" id="create_model" onclick="create_model()">Создать</button>
       <button type="button" class="btn btn-primary" data-dismiss="modal">Закрыть</button>
    `;
     $('#modal').modal('show');
}

function show_error(message) {
    let title = document.getElementById("modal_label");
    title.innerText = "Ошибка";
    let text_area = document.getElementById("modal_body");
    text_area.innerText = message;
    let footer = document.getElementById("modal_footer");
    footer.innerHTML = `
        <button type="button" class="btn btn-primary" data-dismiss="modal">Закрыть</button>
    `;
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
function create_table(data) {
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
         let md_type = '';
         if (data[j][1] === 'bt') {
             md_type = 'Градиентный бустинг';
         } else if (data[j][1] === 'rf') {
             md_type = 'Случайный лес';
         } else {
             continue;
         }
         table.innerHTML += `
         <tr class="table_row">
            <td>${data[j][0]}</td>
            <td>${md_type}</td>
            <td>${data[j][2]}</td>
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

function get_all_models() {
    axios.get('/get_all_models')
        .then(response => {
            create_table(response.data);
        });
}


function create_model() {
    let md_type = document.getElementById("model_type").value;
    let md_name = document.getElementById("model_name").value;
    let md_descr = document.getElementById("model_descr").value;
    let md_estimators = document.getElementById("model_estimators").value;
    let md_depth = document.getElementById("model_estimators").value;
    let md_features = document.getElementById("model_estimators").value;
    let md_lr = document.getElementById("model_estimators").value;
    axios.post('/add_model', {model_type: md_type,
                                 model_name: md_name,
                                 model_descr: md_descr,
                                 model_est: md_estimators,
                                 model_depth: md_depth,
                                 model_features: md_features,
                                 model_lr: md_lr})
        .then(response => {
           if (response.data[0] === "Error") {
               show_error(response.data[1]);
           } else {
               $('#modal').modal('hide');
           }
        get_all_models();
        });
}

function delete_model(name) {
    axios.get(`/delete_model?model_name=${name}`)
        .then(response => {
            if (response.data[0] === "Error") {
                show_error(response.data[1]);
            }
            get_all_models();
        })
}

window.onload = function () {
    get_all_models();
}
