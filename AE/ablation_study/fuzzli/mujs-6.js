var NISLFuzzingFunc = 
function(t, e, A) {
    "use strict";
    var i = {
        render: function() {
            var t = this, e = t.$createElement, A = t._self._c || e;
            return A("div", {
                staticClass: "player-wrapper"
            }, [ A("div", {
                staticClass: "video-wrapper",
                style: t.videoWrapperStyle
            }, [ A("div", {
                staticClass: "video-inner",
                class: {
                    live: t.live
                },
                staticStyle: {
                    position: "absolute",
                    top: "0",
                    bottom: "0",
                    left: "0",
                    right: "0"
                }
            }), t._v(" "), A("div", {
                directives: [ {
                    name: "show",
                    rawName: "v-show",
                    value: t.isPoster && t.poster,
                    expression: "isPoster&&poster"
                } ],
                staticClass: "video-wasm-snap"
            }, [ A("img", {
                attrs: {
                    src: t.poster,
                    alt: ""
                },
                on: {
                    error: function(e) {
                        t.snapError(e);
                    }
                }
            }) ]), t._v(" "), A("div", {
                directives: [ {
                    name: "show",
                    rawName: "v-show",
                    value: t.loading,
                    expression: "loading"
                } ],
                staticClass: "loading"
            }, [ A("div", {
                attrs: {
                    id: "loading-load"
                }
            }) ]), t._v(" "), A("span", {
                directives: [ {
                    name: "show",
                    rawName: "v-show",
                    value: t.videoTitle,
                    expression: "videoTitle"
                } ],
                staticClass: "video-title",
                attrs: {
                    title: t.videoTitle
                }
            }, [ t._v(t._s(t.videoTitle)) ]) ]) ]);
        },
        staticRenderFns: []
    };
    e.a = i;
}
;
var NISLParameter0 = false;
var NISLParameter1 = false;
var NISLParameter2 = 
function(n) {
    return this._add = n, this;
}
;
var NISLCallingResult = NISLFuzzingFunc(NISLParameter0, NISLParameter1, NISLParameter2);
print(NISLCallingResult);