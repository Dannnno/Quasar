(function() {
    window.google = {
        kEI: '5zaNVP-WEYzboAT0rIKYBA',
        kEXPI: '4011559,4013605,4014789,4016824,4017578,4020347,4020562,4021598,4022506,4023567,4023677,4025103,4025182,4025768,4025828,4026559,4026619,8300096,8300098,8500393,8500885,8500923,10200083,10200716,10200764,10200834',
        authuser: 0,
        kSID: '5zaNVP-WEYzboAT0rIKYBA'
    };
    google.kHL = 'en';
})();
(function() {
    google.lc = [];
    google.li = 0;
    google.getEI = function(a) {
        for (var b; a && (!a.getAttribute || !(b = a.getAttribute("eid"))); ) a = a.parentNode;
        return b || google.kEI;
    };
    google.https = function() {
        return "https:" == window.location.protocol;
    };
    google.ml = function() {

    };
    google.time = function() {
        return new Date().getTime();
    };
    google.log = function(a, b, d, e, k) {
        var c = new Image(), h = google.lc, f = google.li, g = "", l = google.ls || "";
        c.onerror = c.onload = c.onabort = function() {
            delete h[f];
        };
        h[f] = c;
        d || -1 != b.search("&ei=") || (e = google.getEI(e), g = "&ei=" + e, e != google.kEI && (g += "&lei=" + google.kEI));
        a = d || "/" + (k || "gen_204") + "?atyp=i&ct=" + a + "&cad=" + b + g + l + "&zx=" + google.time();
        /^http:/i.test(a) && google.https() ? (google.ml(Error("a"), !1, {
            src: a,
            glmm: 1
        }), delete h[f]) : (c.src = a, google.li = f + 1);
    };
    google.y = {
    };
    google.x = function(a, b) {
        google.y[a.id] = [a,b];
        return !1;
    };
    google.load = function(a, b, d) {
        google.x({
            id: a + m++
        }, function() {
            google.load(a, b, d);
        });
    };
    var m = 0;
})();
google.kCSI = {
};
var _gjwl = location;
function _gjuc() {
    var a = _gjwl.href.indexOf("#");
    if (0 <= a && (a = _gjwl.href.substring(a), 0 < a.indexOf("&q=") || 0 <= a.indexOf("#q=")) && (a = a.substring(1), -1 == a.indexOf("#"))) {
        for (var d = 0; d < a.length; ) {
            var b = d;
            "&" == a.charAt(b) && ++b;
            var c = a.indexOf("&", b);
            -1 == c && (c = a.length);
            b = a.substring(b, c);
            if (0 == b.indexOf("fp=")) a = a.substring(0, d) + a.substring(c, a.length), c = d; else if ("cad=h" == b) return 0;
            d = c;
        }
        _gjwl.href = "/search?" + a + "&cad=h";
        return 1;
    }
    return 0;
}
function _gjh() {
    !_gjuc() && window.google && google.x && google.x({
        id: "GJH"
    }, function() {
        google.nav && google.nav.gjh && google.nav.gjh();
    });
}
;
window._gjh && _gjh();