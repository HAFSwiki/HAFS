package route

import (
	"encoding/json"
	"log"
	"opennamu/route/tool"
)

func Api_setting_edit(call_arg []string) string {
	db_set := map[string]string{}
	json.Unmarshal([]byte(call_arg[0]), &db_set)

	other_set := map[string]string{}
	json.Unmarshal([]byte(call_arg[1]), &other_set)

	db := tool.DB_connect(db_set)
	defer db.Close()

	auth_name := tool.Get_user_auth(db, db_set, other_set["ip"])
	auth_info := tool.Get_auth_group_info(db, db_set, auth_name)

	if _, ok := auth_info["owner"]; ok {
		stmt, err := db.Prepare(tool.DB_change(db_set, "delete from other where name = ?"))
		if err != nil {
			log.Fatal(err)
		}
		defer stmt.Close()

		_, err = stmt.Exec(other_set["set_name"])
		if err != nil {
			log.Fatal(err)
		}

		stmt, err = db.Prepare(tool.DB_change(db_set, "insert into other (name, data, coverage) values (?, ?, '')"))
		if err != nil {
			log.Fatal(err)
		}
		defer stmt.Close()

		_, err = stmt.Exec(other_set["set_name"], other_set["data"])
		if err != nil {
			log.Fatal(err)
		}

		return_data := make(map[string]interface{})
		return_data["response"] = "ok"

		json_data, _ := json.Marshal(return_data)
		return string(json_data)
	} else {
		return_data := make(map[string]interface{})
		return_data["response"] = "require auth"

		json_data, _ := json.Marshal(return_data)
		return string(json_data)
	}
}
