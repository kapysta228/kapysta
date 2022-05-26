if (document.getElementById('app_new_operation')){
    var app_new_operation = new Vue({
        el: "#app_new_operation",
        data: {
            state_radio: 0,
            options: [],
        },

        mounted(){
            var request = sendRequest('/ajax/category/?type_pay=' + this.state_radio + '', 'get').then((response)=>{
                this.options = response.data.categories;
            })
        },

        methods: {
            radio_changed(){
                var request = sendRequest('/ajax/category/?type_pay=' + this.state_radio + '', 'get').then((response)=>{
                this.options = response.data.categories;
                })
            }
        }
    });
}

if (document.getElementById('app_update_operation')){
    var app_update_operation = new Vue({
        el: '#app_update_operation',
        data: {
            state_radio: 0,
            options: [],
            instance: 0,
        },
        mounted(){
            this.state_radio = document.getElementById('type_pay').value;
            this.instance = document.getElementById('instance').value;
            var request = sendRequest('/ajax/category/?type_pay=' + this.state_radio + '', 'get').then((response)=>{
                this.options = response.data.categories;
            })
        },
         methods: {
            radio_changed(){
                var request = sendRequest('/ajax/category/?type_pay=' + this.state_radio + '', 'get').then((response)=>{
                this.options = response.data.categories;
                console.log(response.data.categories);
                })
            },
        },

    });
}

if (document.getElementById('app_category')){
    var app_category = new Vue({
        el: '#app_category',
        methods: {
            delete_category(id, name){
                sendRequest('/ajax/'+id+'/delete/', 'post').then((response)=>{
                    console.log(response.data)
                    if (response.data.result == 'ok'){
                        location.reload();
                    }
                });
            },

            delete_operation(id, url){
                sendRequest(url, 'post').then((response)=>{
                    console.log(response.data)
                    if (response.data.result == 'ok'){
                        location.reload();
                    }
                });
            }
        }
    });
}

if (document.getElementById('app-statistic')){
    var app_statistic = new Vue({
        el: '#app-statistic',
        data: {
            state_calendar: 0,
            state_radio: 0,
            chart: null,
            data_is_empty: false,
            calendar_date: null,
        },
        methods: {
            get_format(){
                 var get_parameters = '';
                 if (this.state_calendar=='1'){
                    get_parameters += '?year=' + this.calendar_date;//document.getElementById('date-by-year').value;
                 }else{
                    date = this.calendar_date.split('-');//document.getElementById('date-by-year-month').value.split('-');
                    get_parameters += '?year=' + date[0] + '&month=' + date[1];
                 }
                 get_parameters += '&type_pay=' + this.state_radio;
                 return get_parameters;
            },
            current_date(){
                var now = new Date();
                return (now.toLocaleString("en-US", {year: 'numeric'}) + '-' +now.toLocaleString("en-US", {month: '2-digit'}));
            },
            current_year(){
                var now = new Date();
                return (now.toLocaleString('en-Us', {year: 'numeric'}));
            },
            create_chart(){
                var ctx = document.getElementById('chart')//.getContext('2d');
                this.chart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: [],
                        datasets: [{
                            label: '',
                            data: [],
                            backgroundColor: [],
                    }]},
                    options: {
                        responsive: true,
                        legend: {
                            position: 'left',
                            labels: {
                                fontSize: 14,

                            },
                        },
                        plugins: {
                            datalabels: {
                                padding: {
                                    left: 5,
                                    right: 5,
                                },
                                font: {
                                    size: 14,
                                },
                                color: '#fff',
                                offset: -10,
                                borderWidth: 1,
                                borderRadius: 25,

                                borderColor: '#fff',
                                backgroundColor: (context) => {
                                    return context.dataset.backgroundColor
                                 },

                               formatter: function(value, context) {
                                    total = sum(context.dataset.data)
                                    return Math.round(value / total * 100, 2) + '%';
                               }
                            }
                        }
                    }

                });
                this.update_chart();
            },

            radio_changed(){
                this.update_chart();
            },

            type_date_changed(){
                if (this.state_calendar=='1'){
                    this.calendar_date = this.current_year();
                }else{
                    this.calendar_date = this.current_date();
                }
                this.update_chart();
            },

            date_change(){
                this.update_chart();
            },

            update_chart(){
                sendRequest('/ajax/chart/' + this.get_format(), 'get').then((response)=>{
                    if (response.data.data.length > 0){
                        this.data_is_empty = false;
                    }else{
                        this.data_is_empty = true;
                    }

                    this.chart.data.labels = [];
                    this.chart.data.datasets[0].data = [];
                    this.chart.data.datasets[0].backgroundColor = [];

                    for (var item in response.data.data){
                        item = response.data.data[item]
                        this.chart.data.labels.push(item.category__name);
                        this.chart.data.datasets[0].data.push(parseFloat(item.total));
                        this.chart.data.datasets[0].backgroundColor.push(item.color);
                    }
                    this.chart.update();

                });
            },
        },
        mounted(){
            this.calendar_date = this.current_date();
            this.create_chart();
        }

});
}

if (document.getElementById('family-chart')){
    var app_family_chart = new Vue({
    el: '#family-chart',
    data: {
            state_calendar: 0,
            state_radio: 0,
            chart: null,
            chart_user: null,
            data_is_empty: false,
            calendar_date: null,
        },
        methods: {
            get_format(){
                 var get_parameters = '';
                 if (this.state_calendar=='1'){
                    get_parameters += '?year=' + this.calendar_date;//document.getElementById('date-by-year').value;
                 }else{
                    date = this.calendar_date.split('-');//document.getElementById('date-by-year-month').value.split('-');
                    get_parameters += '?year=' + date[0] + '&month=' + date[1];
                 }
                 get_parameters += '&type_pay=' + this.state_radio;
                 return get_parameters;
            },
            current_date(){
                var now = new Date();
                return (now.toLocaleString("en-US", {year: 'numeric'}) + '-' +now.toLocaleString("en-US", {month: '2-digit'}));
            },
            current_year(){
                var now = new Date();
                return (now.toLocaleString('en-Us', {year: 'numeric'}));
            },
            create_chart(){
                var ctx = document.getElementById('chart_category')//.getContext('2d');
                this.chart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: [],
                        datasets: [{
                            label: '',
                            data: [],
                            backgroundColor: [],
                    }]},
                    options: {
                        responsive: true,
                        legend: {
                            position: 'top',
                            labels: {
                                fontSize: 14,

                            },
                        },
                        plugins: {
                            datalabels: {
                                padding: {
                                    left: 5,
                                    right: 5,
                                },
                                font: {
                                    size: 14,
                                },
                                color: '#fff',
                                offset: -10,
                                borderWidth: 1,
                                borderRadius: 25,

                                borderColor: '#fff',
                                backgroundColor: (context) => {
                                    return context.dataset.backgroundColor
                                 },

                               formatter: function(value, context) {
                                    total = sum(context.dataset.data)
                                    return Math.round(value / total * 100, 2) + '%';
                               }
                            }
                        }
                    }

                });

                this.chart_user = new Chart(document.getElementById('chart_user'), {
                    type: 'doughnut',
                    data: {
                        labels: [],
                        datasets: [{
                            label: '',
                            data: [],
                            backgroundColor: [],
                    }]},
                    options: {
                        responsive: true,
                        legend: {
                            position: 'top',
                            labels: {
                                fontSize: 14,

                            },
                        },
                        plugins: {
                            datalabels: {
                                padding: {
                                    left: 5,
                                    right: 5,
                                },
                                font: {
                                    size: 14,
                                },
                                color: '#fff',
                                offset: -10,
                                borderWidth: 1,
                                borderRadius: 25,

                                borderColor: '#fff',
                                backgroundColor: (context) => {
                                    return context.dataset.backgroundColor
                                 },

                               formatter: function(value, context) {
                                    total = sum(context.dataset.data)
                                    return Math.round(value / total * 100, 2) + '%';
                               }
                            }
                        }
                    }

                });

                this.update_chart();
            },

            radio_changed(){
                this.update_chart();
            },

            type_date_changed(){
                if (this.state_calendar=='1'){
                    this.calendar_date = this.current_year();
                }else{
                    this.calendar_date = this.current_date();
                }
                this.update_chart();
            },

            date_change(){
                this.update_chart();
            },

            update_chart(){
                sendRequest('/ajax/family/operations/' + this.get_format(), 'get').then((response)=>{
                    if (response.data.categories.length > 0){
                        this.data_is_empty = false;
                    }else{
                        this.data_is_empty = true;
                    }

                    this.chart.data.labels = [];
                    this.chart.data.datasets[0].data = [];
                    this.chart.data.datasets[0].backgroundColor = [];

                    this.chart_user.data.labels = [];
                    this.chart_user.data.datasets[0].data = [];
                    this.chart_user.data.datasets[0].backgroundColor = [];

                    for (var item in response.data.categories){
                        item = response.data.categories[item]
                        this.chart.data.labels.push(item._category);
                        this.chart.data.datasets[0].data.push(parseFloat(item.total));
                        this.chart.data.datasets[0].backgroundColor.push(item.color);
                    }

                    for (var item in response.data.users){
                        item = response.data.users[item]
                        this.chart_user.data.labels.push(item._user);
                        this.chart_user.data.datasets[0].data.push(parseFloat(item.total));
                        this.chart_user.data.datasets[0].backgroundColor.push(item.color);
                    }

                    this.chart.update();
                    this.chart_user.update();

                });
            },
        },
        mounted(){
            this.calendar_date = this.current_date();
            this.create_chart();
        }
});
}

if (document.getElementById('app-operation')){
    var app_operations = new Vue({
    el: '#app-operations',
    data: {
        operations: [],
        total: 0,
        current_month: null,
    },
    methods: {
        month_changed(){
            this.reload_operations();
        },
        reload_operations(){
            sendRequest('/ajax/operations/?month=' + this.current_month, 'get').then((response)=>{
            this.operations = response.data.operations;
            this.total = parseFloat(response.data.total);
            });
        },
        delete_operation(id, index){
            sendRequest('/operation/' + id + '/delete/', 'post').then((response)=>{
                if (response.data.result == 'ok'){
                    console.log(this.operations[index].category__type_pay);
                    if (this.operations[index].category__type_pay == 1){
                        this.total -= parseFloat(this.operations[index].value);
                    }else{
                        this.total += parseFloat(this.operations[index].value);
                    }
                    this.operations.splice(index, 1);
                }
            })
        },
        update_operation(id){
            $('#modal-finance').modal('show');
        }
    },
    mounted(){
        this.current_month = current_month();
        this.reload_operations();
    },
});
}



function current_month(){
    var now = new Date();
    return now.toLocaleString("en-US", {year: 'numeric'}) + '-' +now.toLocaleString("en-US", {month: '2-digit'});
}

function sendRequest(url, method, data){
    var request = axios({
        method: method,
        url: url,
        data: data,
        xsrfCookieName: 'csrftoken',
        xsrfHeaderName: 'X-CSRFToken',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    return request
}

function month_change(value, url){
    atrs = value.split('-');
    document.location.href = url+'?year=' + atrs[0] + '&month=' + atrs[1];
}

function sum(array){
    const reducer = (accumulator, currentValue) => accumulator + currentValue;
    return array.reduce(reducer);
}

function open_modal_dialog(){
    $('#modal-finance').modal('show');
}

function delete_operation(id){
    sendRequest('/operation/' + id + '/delete/', 'get').then((response)=>{
        if (response.data.result == 'ok'){
            location.reload();
        }
    });
}
