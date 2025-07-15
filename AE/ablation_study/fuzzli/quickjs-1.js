for (var INDEX = 0; INDEX < 1000; INDEX++) {
    var NISLFuzzingFunc = function (config) {
        var self = this;
        self.image = config.image;
        self.grid = config.grid;
        self.frame = config.frame;
        self.anchor = {};
        config.anchor = config.anchor || {};
        self.anchor.x = config.anchor.x || 0;
        self.anchor.y = config.anchor.y || 0;
        self.currentFrame = 0;
        self.currentFrameName = '';
        self.frameNames = config.frameNames || [];
        self.gotoFrame = function (index) {
            self.currentFrame = index;
            self.currentFrameName = self.frameNames[self.currentFrame] || '';
        };
        self.nextFrame = function () {
        };
        self.gotoFrameByName = function (name) {
        };
        self.doesFrameNameExist = function (name) {
        };
        self.gotoFrame(0);
        self.x = config.x || 0;
        self.y = config.y || 0;
        self.rotation = config.rotation || 0;
        self.scale = config.scale || 1;
        self.squash = config.squash || 1;
        self.alpha = config.alpha || 1;
        self.visible = true;
        self.draw = function (ctx) {
        };
    };
}
var NISLParameter0 = '~[td2OJHL85 "4ttN91K%Q]Z5c!"8y:11r)S1DA.6eTx^|1~7TgPOTQ6u,W[A$fDhSgZ7ofwAuH7Ur%3i,zyfL=u`!n9-&_jEfI@sp/kMR]*zU"[z2p5WqQ+~x0_';
var NISLCallingResult = NISLFuzzingFunc(NISLParameter0);
print(NISLCallingResult);