//****************针对第二种方式的具体js实现部分******************//
//****************所使用的数据是city.js******************//

/*根据id获取对象*/
function $(str) {
    return document.getElementById(str);
}

var addrShow = $('addr-show');  //最终地址显示框
var titleWrap = $('title-wrap').getElementsByTagName('LI');
var addrWrap = $('addr-wrap');   //省市区显示模块
var btn = document.getElementsByClassName('met')[0];  //确定按钮

var current = {
    prov: '',
    city: '',
    country: '',
    provVal: '',
    cityVal: '',
    countryVal: ''
};

/*自动加载省份列表*/
window.onload = showProv();

function showProv() {
    addrWrap.innerHTML = '';
    /*addrShow.value = '';*/
    btn.disabled = true;
    titleWrap[0].className = 'titleSel';

    $.ajax({url:"{{ url_for('user.area_get') }}", {req_type:"1"},
        function(data){
            console.log(data)
        });
    var len = provice.length;
    for (var i = 0; i < len; i++) {
        var provLi = document.createElement('li');
        provLi.innerText = provice[i]['name'];
        provLi.index = i;
        addrWrap.appendChild(provLi);
    }
}

/*************************需要给动态生成的li绑定点击事件********************** */
addrWrap.onclick = function (e) {
    var n;
    var e = e || window.event;
    var target = e.target || e.srcElement;
    if (target && target.nodeName == 'LI') {
        /*先判断当前显示区域显示的是省市区的那部分*/
        for (var z = 0; z < 3; z++) {
            if (titleWrap[z].className == 'titleSel')
                n = z;
        }
        /*显示的处理函数*/
        switch (n) {
            case 0:
                showCity(target.index);
                break;
            case 1:
                showCountry(target.index);
                break;
            case 2:
                selectCountry(target.index);
                break;
            default:
                showProv();
        }
    }
};

/*选择省份之后显示该省下所有城市*/
function showCity(index) {
    addrWrap.innerHTML = '';
    current.prov = index;
    current.provVal = provice[index].name;
    titleWrap[0].className = '';
    titleWrap[1].className = 'titleSel';
    var cityLen = provice[index].city.length;
    for (var j = 0; j < cityLen; j++) {
        var cityLi = document.createElement('li');
        cityLi.innerText = provice[index].city[j].name;
        cityLi.index = j;
        addrWrap.appendChild(cityLi);
    }
}

/*选择城市之后显示该城市下所有县区*/
function showCountry(index) {
    addrWrap.innerHTML = '';
    current.city = index;
    current.cityVal = provice[current.prov].city[index].name;
    titleWrap[1].className = '';
    titleWrap[2].className = 'titleSel';
    var countryLen = provice[current.prov].city[index].districtAndCounty.length;
    if (countryLen == 0) {
        addrShow02.value = current.provVal + '-' + current.cityVal;
    }
    for (var k = 0; k < countryLen; k++) {
        var cityLi = document.createElement('li');
        cityLi.innerText = provice[current.prov].city[index].districtAndCounty[k];
        cityLi.index = k;
        addrWrap.appendChild(cityLi);
    }
}

/*选中具体的县区*/
function selectCountry(index) {
    btn.disabled = false;
    current.country = index;
    addrWrap.getElementsByTagName('li')[index].style.backgroundColor = '#23B7E5';
    current.countryVal = provice[current.prov].city[current.city].districtAndCounty[index];
}

/*点击确定后恢复成初始状态，且将所选地点显示在输入框中*/
btn.onclick = function () {
    addrShow.value = current.provVal + ' ' + current.cityVal + ' ' + current.countryVal;
    addrWrap.getElementsByTagName('li')[current.country].style.backgroundColor = '';
};

/*分别点击省市区标题的处理函数*/
document.getElementById('title-wrap').onclick = function (e) {
    var e = e || window.event;
    var target = e.target || e.srcElement;
    if (target && target.nodeName == 'LI') {
        for (var z = 0; z < 3; z++) {
            titleWrap[z].className = '';
        }
        target.className = 'titleSel';
        if (target.value == '0') {
            showProv();
        } else if (target.value == '1') {
            showCity(current.prov);
        } else {
            showCountry(current.city);
        }
    }
};