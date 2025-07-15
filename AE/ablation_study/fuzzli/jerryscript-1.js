var NISLFuzzingFunc = function (memo, x, i, list) {
    var curr = x;
    var next = list.length - i > 1 ? list[i + 1] : curr;
    next = JSON.parse(JSON.stringify(next));
    curr.push(i);
    next.push(i);
    next[3] = curr[3];
    return memo.concat([
        curr,
        next
    ]);
};
var NISLParameter0 = [
    function () {
        return {
            name: 'Spicy Times',
            desc: 'This upgrade gives you a chance for bonus Imagination when using the Spice Mill. Grind it out!',
            max_uses: 1,
            chance: 5,
            cost: 200,
            config: {
                bg: 'lightnavy',
                pattern: 'skill',
                suit: 'skill',
                art: 'skill_spicemilling',
                icon: 'imagination'
            },
            conditions: [{
                    type: 4,
                    data: { skill_id: 'spicemilling_1' }
                }],
            rewards: []
        };
    },
    null,
    undefined,
    false,
    -4506.803435174716,
    null
];
var NISLParameter1 = [
    function (v) {
        this._setProperty('-webkit-animation-timing-function', v);
    },
    function (mat, angle) {
        var c = Math.cos(angle);
        var s = Math.sin(angle);
        mat[0] = c;
        mat[1] = 0;
        mat[2] = -s;
        mat[3] = 0;
        mat[4] = 0;
        mat[5] = 1;
        mat[6] = 0;
        mat[7] = 0;
        mat[8] = s;
        mat[9] = 0;
        mat[10] = c;
        mat[11] = 0;
        mat[12] = 0;
        mat[13] = 0;
        mat[14] = 0;
        mat[15] = 1;
        return mat;
    },
    function (key) {
        return this.has(key) ? this.pris[key] : null;
    },
    function (t, e, n) {
        'use strict';
        Object.defineProperty(e, '__esModule', { value: !0 }), e.default = void 0, n('c5f6');
        var i = {
            name: 'UniSegmentedControl',
            props: {
                current: {
                    type: Number,
                    default: 0
                },
                values: {
                    type: Array,
                    default: function () {
                        return [];
                    }
                },
                activeColor: {
                    type: String,
                    default: '#007aff'
                },
                styleType: {
                    type: String,
                    default: 'button'
                }
            },
            data: function () {
                return { currentIndex: 0 };
            },
            watch: {
                current: function (t) {
                    t !== this.currentIndex && (this.currentIndex = t);
                }
            },
            created: function () {
                this.currentIndex = this.current;
            },
            methods: {
                _onClick: function (t) {
                    this.currentIndex !== t && (this.currentIndex = t, this.$emit('clickItem', t));
                }
            }
        };
        e.default = i;
    },
    function () {
        var sCurrIndex = this.aCurrObjNames['index'];
        if (sCurrIndex != null && sCurrIndex != undefined && sCurrIndex.length > 0) {
            var bReturn = this.mDb.reindexObject('INDEX', sCurrIndex);
            return bReturn;
        }
        return false;
    },
    function () {
        this.head = new this.headClass();
    },
    function ($p0) {
        while ($p0.firstChild) {
            $p0.removeChild($p0.firstChild);
        }
    }
];
var NISLParameter2 = '2m,XiR3gltyuez[(vO+G[13D[CX$Kuq)$DX,O1=z=QoS:q^@[uGx09410l+{DIL&v@RWUaHlW)/@[veMzmw*fcg8g4nO9!W_aa0e7&\'#GFiobTbVm!5_GX<x N';
var NISLParameter3 = [
    function (a) {
        return a.overlays;
    },
    function (start, length, size) {
        var offsetLeft = (start + length) % 8;
        var offsetRight = start % 8;
        var curByte = size - (start >> 3) - 1;
        var lastByte = size + (-(start + length) >> 3);
        var diff = curByte - lastByte;
        var sum = this._readByte(curByte, size) >> offsetRight & (1 << (diff ? 8 - offsetRight : length)) - 1;
        if (diff && offsetLeft)
            sum += (this._readByte(lastByte++, size) & (1 << offsetLeft) - 1) << (diff-- << 3) - offsetRight;
        while (diff)
            sum += this._shl(this._readByte(lastByte++, size), (diff-- << 3) - offsetRight);
        return sum;
    },
    function (lines, points, locGeom) {
        for (var i = 0; i < lines.length; i++) {
            var line = lines[i];
            for (var j = 0; j < points.length; j++) {
                var pt = points[j];
                this.computeMinDistance(line, pt, locGeom);
                if (this.minDistance <= this.terminateDistance)
                    return;
            }
        }
    },
    function (pc, msg, suppress_activity) {
        pc.sendMsgOnline({
            type: 'snap_travel_screen',
            text: 'In Soviet ' + pc.location.label + ', picture takes you!'
        });
    },
    function (value) {
        if (typeof value == 'string')
            this._acceptedDataTypes = value.split(',');
        else
            this._acceptedDataTypes = value;
    }
];
for (var INDEX = 0; INDEX < 1000; INDEX++) {
    var NISLCallingResult = NISLFuzzingFunc(NISLParameter0, NISLParameter1, NISLParameter2, NISLParameter3);
}
print(NISLCallingResult);