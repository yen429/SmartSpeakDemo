const fs = require("fs");
const dialogStatePath = __dirname + "/../dialog_state";
const cardDataPath = __dirname + "/../card_data";
var old_state = "";
var old_data = "";


module.exports = {
    set_dialog: function(state) {
        if (old_state == state) {
            return;
        }

        old_state = state;
        if(fs.existsSync(dialogStatePath)) {
            fs.writeFileSync(dialogStatePath, state + "\n");
            console.log("Update dialog_state to " + state);
        }
    },
    set_card: function(data) {
        if (old_data == data) {
           return;
        }

        old_data = data;
        if(fs.existsSync(cardDataPath)) {
            fs.writeFileSync(cardDataPath, JSON.stringify(data, null, 2) + "\n");
        }
    }
};

