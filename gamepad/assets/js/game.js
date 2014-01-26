
var player;

!function($) {

    "use strict";

    var game = {
        path: ""
    }

    Crafty.sprite(32, game.path + "/assets/img/sprite.png", {
        PlayerSprite: [0, 0],
    });

    Crafty.scene("Loading",
    function() {

        Crafty.background("#000");

        Crafty.e("2D", "DOM", "Text").css({
            "font-size": "170%",
            "white-space": "nowrap",
            "text-align": "center",
            "color": "#888"
        })
        .attr({
            x: 40,
            y: 40
        })
        .text("Loading...");

        Crafty.load([game.path + "/assets/img/sprite.png"],
        function() {
            Crafty.scene("Game");
        },
        function(e) {},
        function(e) {
            alert('Error while loading assets (loaded ' + e.loaded + ', percent ' + Math.round(e.percent) + ', total ' + e.total + ')');
        }
        );

    });

    Crafty.scene("Game",
    function() {

        Crafty.background("#000");

        Crafty.e("2D, Canvas, Color, Platform, Collision")
        .attr({
            x: 10,
            y: 660,
            w: 780,
            h: 10
        })
        .color("#444");
        Crafty.e("2D, Canvas, Color, Platform, Collision")
        .attr({
            x: 400,
            y: 600,
            w: 390,
            h: 10
        })
        .color("#444");
        Crafty.e("2D, Canvas, Color, Platform, Collision")
        .attr({
            x: 100,
            y: 540,
            w: 200,
            h: 10
        })
        .color("#444");
        Crafty.e("2D, Canvas, Color, Platform, Collision")
        .attr({
            x: 690,
            y: 540,
            w: 100,
            h: 10
        })
        .color("#444");

        Crafty.e("2D, Canvas, Color, Platform, Wall")
        .attr({
            x: 780,
            y: 0,
            w: 10,
            h: 660
        })
        .color("#444");
        Crafty.e("2D, Canvas, Color, Platform, Wall")
        .attr({
            x: 10,
            y: 0,
            w: 10,
            h: 660
        })
        .color("#444");

        player = Crafty.e("Player")
        .attr({
            x: 25,
            y: 600
        });

        $(window).trigger('resize');

    });

    Crafty.c("Player", {
        init: function() {
            this.addComponent("2D", "Canvas", "Gravity", "Twoway", "SpriteAnimation", "PlayerSprite", "Collision", "GamePad")
            .animate("StandingAnimation", [
            [0, 1], [1, 1], [2, 1], [3, 1], [4, 1], [5, 1], [6, 1],
            [7, 1], [0, 2], [1, 2], [2, 2], [3, 2], [4, 2], [5, 2],
            [6, 2], [7, 2], [0, 3], [1, 3], [2, 3], [3, 3], [4, 3], [5, 3], [6, 3], [7, 3]
            ])
            .animate('RightWalking', 0, 5, 7)
            .animate('LeftWalking', 0, 4, 7)
            .animate("StandingAnimation", 10, -1)
            .twoway(3, 5)
            .gravity("Platform")
            .gravityConst(.2)
            .bind("NewDirection",
            function(direction) {
                if (direction.x < 0) {
                    if (!this.isPlaying("LeftWalking")) {
                        this.stop().animate("LeftWalking", 10, -1);
                    }
                } else if (direction.x > 0) {
                    if (!this.isPlaying("RightWalking")) {
                        this.stop().animate("RightWalking", 10, -1);
                    }
                } else {
                    if (!this.isPlaying("StandingAnimation")) {
                        this.stop().animate("StandingAnimation", 10, -1);
                    }
                }
            })
            .bind("Moved",
            function(from) {
                if (this.hit("Wall")) {
                    this.attr({
                        x: from.x,
                        y: from.y
                    });
                }
            });

            return this;
        }
    });

    Crafty.c("GamePad", {
        _left: false,
        _right: false,

        init: function() {},
        gamepad: function() {
            return this;
        },
        jump: function() {
            this._up = true;
        },
        right: function() {
            if (!this._right) {
                this.trigger("KeyDown", {
                    key: 68
                });
                this._right = true;
            }
        },
        left: function() {
            if (!this._left) {
                this.trigger("KeyDown", {
                    key: 65
                });
                this._left = true;
            }
        },
        halt: function() {
            if (this._left) {
                this.trigger("KeyDown", {
                    key: 68
                });
            } else if (this._right) {
                this.trigger("KeyDown", {
                    key: 65
                });
            }

            this.trigger("NewDirection", {
                x: 0
            });

            this._left = false;
            this._right = false;
        }

    });


    /**
    * Init Game
    */
    var WIDTH = 800,
    HEIGHT = 680;

    Crafty.init(WIDTH, HEIGHT);
    Crafty.background("#FFF");

    Crafty.scene("Loading");

    /**
    * Resize Game Area
    */
    $(window).on('resize orientationchange',
    function(event) {

        var widthToHeight = WIDTH / HEIGHT;
        var newWidth = window.innerWidth;
        var newHeight = window.innerHeight;
        var newWidthToHeight = newWidth / newHeight;

        if (newWidthToHeight > widthToHeight) {
            newWidth = newHeight * widthToHeight;
        } else {
            newHeight = newWidth / widthToHeight;
        }

        var marginLeft = (window.innerWidth - newWidth) / 2;

        var $cr = $('#cr-stage');
        var $canvas = $cr.find('canvas');

        $canvas.css({
            'width': newWidth,
            'height': newHeight,
            'margin-left': marginLeft
        });
        $cr.css({
            'width': '100%',
            'height': newHeight
        });
    });

} (window.jQuery);
