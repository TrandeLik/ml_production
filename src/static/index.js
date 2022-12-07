const add_model_show = document.getElementById("add_model");


add_model_show.onclick = function () {
     let title = document.getElementById("modal_label");
     title.innerText = "Создать модель";
     let form = document.getElementById("modal_body");
     form.innerHTML = `
        <div class="form-group">
            <label for="model_type" class="form-label">Тип модели</label>
            <select class="form-select form-control" id="model_type">
                <option value="bt">Бустинг</option>
                <option value="rf">Случайный лес</option>
            </select>
            <label for="model_name" style="margin-top: 1rem" class="form-label">Название модели</label>
            <input type="text" class="form-control" id="model_name">
            <label for="model_descr" style="margin-top: 1rem" class="form-label">Описание модели</label>
            <textarea type="text" class="form-control" id="model_descr" maxlength='300'></textarea>
            <label for="model_estimators" style="margin-top: 1rem" class="form-label">Количество деревьев</label>
            <small class="form-text text-muted">Ничего не вводите для 100 деревьев</small>
            <input type="number" class="form-control" id="model_estimators" min="1">
            <label for="model_depth" style="margin-top: 1rem" class="form-label">Глубина деревьев</label>
            <input type="number" class="form-control" id="model_depth" min="1">
            <small class="form-text text-muted">Ничего не вводите для неограниченной глубины</small>
            <label for="model_features" style="margin-top: 1rem" class="form-label">Размер признакового пространства для каждого дерева</label>
            <input type="number" class="form-control" id="model_features" min="0" max="1" step="0.01">
            <small class="form-text text-muted">Ничего не вводите для значения равного 1/3</small>
            <label for="model_lr" style="margin-top: 1rem" class="form-label">Learning rate</label>
            <input type="number" class="form-control" id="model_lr" min="0" step="0.01">
            <small class="form-text text-muted">Нужно заполнить только для градиентного бустинга. Ничего не вводите для значения 0.1</small>
        </div>
     `;
     let footer = document.getElementById("modal_footer");
     footer.innerHTML = `
       <button type="button" class="btn btn-success" onclick="create_model()">Создать</button>
       <button type="button" class="btn btn-primary" data-bs-dismiss="modal">Закрыть</button>
    `;
     $('#modal').modal('show');
}

function show_message(title_text, message) {
    let title = document.getElementById("modal_label");
    title.innerText = title_text;
    let text_area = document.getElementById("modal_body");
    text_area.innerText = message;
    let footer = document.getElementById("modal_footer");
    footer.innerHTML = `
        <button type="button" class="btn btn-primary" data-bs-dismiss="modal">Закрыть</button>
    `;
    $('#modal').modal('show');
}

function show_fit_model(name) {
    let title = document.getElementById("modal_label");
    title.innerText = "Обучить модель";
    let form = document.getElementById("modal_body");
     form.innerHTML = `
        <div class="form-group">
            <label for="train_data" class="form-label">Файл с обучающей выборкой</label>
            <input class="form-control" type="file" id="train_data" accept=".csv">
            <label for="train_data" class="form-label" style="margin-top: 1rem">Файл с валидационной выборкой</label>
            <input class="form-control" type="file" id="val_data" accept=".csv">
            <small class="form-text text-muted">Опционально</small>
            <label for="train_data" class="form-label" style="margin-top: 1rem">Название колонки с целевой переменной</label>
            <input class="form-control" type="text" id="target_column">
            <label for="train_data" class="form-label" style="margin-top: 1rem">Описание данных</label>
            <textarea class="form-control" id="data_description" maxlength='300'></textarea>
            <p style="margin-top: 1.5rem">После нажатия кнопки "Обучить" дождитесь появления сообщения об окончании обучения</p>
        </div>
     `;
     let footer = document.getElementById("modal_footer");
     footer.innerHTML = `
       <button type="button" class="btn btn-warning" onclick="fit_model('${name}')">Обучить</button>
       <button type="button" class="btn btn-primary" data-bs-dismiss="modal">Закрыть</button>
    `;
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
    let md_depth = document.getElementById("model_depth").value;
    let md_features = document.getElementById("model_features").value;
    let md_lr = document.getElementById("model_lr").value;
    axios.post('/add_model', {model_type: md_type,
                                 model_name: md_name,
                                 model_descr: md_descr,
                                 model_est: md_estimators,
                                 model_depth: md_depth,
                                 model_features: md_features,
                                 model_lr: md_lr})
        .then(response => {
           if (response.data[0] === "Error") {
               show_message("Ошибка", response.data[1]);
           } else {
               $('#modal').modal('hide');
           }
        get_all_models();
        }).catch(error => {
            show_message("Ошибка", "Проверьте корректность введенных данных");
        });
}

function delete_model(name) {
    axios.get(`/delete_model?model_name=${name}`)
        .then(response => {
            if (response.data[0] === "Error") {
                show_message("Ошибка", response.data[1]);
            }
            get_all_models();
        }).catch(error => {
            show_message("Ошибка", "Что-то пошло не так, попробуйте удалить модель еще раз");
    });
}

function fit_model(name) {
    let data = new FormData();
    let train = document.getElementById("train_data");
    let val = document.getElementById("val_data");
    let target = document.getElementById("target_column");
    let description = document.getElementById("data_description")
    data.append("train", train.files[0]);
    data.append("val", val.files[0]);
    data.append("target", target.value);
    data.append("model", name);
    data.append("data_description", description.value);
    axios.post("/fit_model", data, {
         headers: {
            "Content-Type": "multipart/form-data",
         }})
        .then(response => {
          if (response.data[0] === "Error") {
              show_message("Ошибка", response.data[1]);
          } else {
              show_message("Успех", "Информацию об обучении теперь можно посмотреть по нажатию кнопки Подробнее");
          }
          get_all_models();
        }).catch(error => {
            show_message("Ошибка", "Не удалось обучить модель");
    });
}

window.onload = function () {
    get_all_models();
}
