from cosmicfrog import FrogModel

def main():
    # EXAMPLE: Init model class
    app_key="op_MGMyODQzZjMtYWRkZC00ZjI2LThjY2ItY2VkYTBkNGJlZjhm"
    frog_model = FrogModel(app_key=app_key, model_name="demo")

    # BUG 1
    # res = frog_model.run_scenario(['Baseline with DBR'], fire_and_forget=True, check_configuration_before_run=True)

    # BUG2
    # res = frog_model.run_scenario(['all'], fire_and_forget=True, check_configuration_before_run=True)

    # res = frog_model.run_scenario(['Baseline'], fire_and_forget=True, check_configuration_before_run=True)

    # run = frog_model.run_scenario(['Baseline'], fire_and_forget=True)
    # print(res)

    # This is how it would scenario configuration would need to look
    # scenarios_with_custom_configuration = [
    #     {
    #         "scenario_name": "Baseline",
    #         "engine": "neo",
    #         "resource_size": "s",
    #     },
    #     {
    #         "scenario_name": "No Detroit DC",
    #         "engine": "neo",
    #         "resource_size": "s",
    #     },
    #     {
    #         "scenario_name": "GF 9 Facilities",
    #         "engine": "neo",
    #         "resource_size": "m",
    #     },
    #     {
    #         "scenario_name": "Throg Example",
    #         "engine": "throg",
    #         "resource_size": "m",
    #     },
    # ]

    # response = frog_model.run_multiple_scenarios_with_custom_configuration(
    #     scenarios_with_custom_configuration=scenarios_with_custom_configuration
    # )
    # print(response)



    ## NOVO:
    # Example -> run scenario, fetch jobs from solver, tail job records live

    # run = frog_model.run_scenario(['Baseline'], fire_and_forget=True)
    # run = frog_model.run_scenario(['No Detroit DC', 'GF 9 Facilities', 'Throg Example', 'Hopper Example', 'No Flow Constraints', 'GF 10 Facilities'], fire_and_forget=True)
    # print('-- scenarioRunFinished', run)
    # solver_job_key = run['job_keys']['neo']
    # print('-- solver_job_key', solver_job_key)
    # jobs_from_solver = frog_model.get_all_jobs_for_solver_job(job_key=solver_job_key)
    # print('-- jobs_from_solver', jobs_from_solver)
    # for job in jobs_from_solver['jobs']:
    #     print('-- tail_job_records', job)
    #     res = frog_model.tail_job_records(job_key=job['jobKey'])
    #     print(res)


    # example -> run scenario, wait to finish -> fetch jobs -> fetch logs and records


    # example -> how to fetch error from scenario


    ### Model management Start

    # Get All Model Templates - static
    # abc = FrogModel.all_available_model_templates(app_key=app_key)
    # print(abc)

    # Get All Models - static
    # res = FrogModel.all_models(app_key=app_key)
    # print(res)

    # New Model - static
    # res = FrogModel.create_model(app_key=app_key, name="1111121312341122")
    # print('res', res)

    # Edit Model
    # frog_model = FrogModel(app_key=app_key, model_name="IKEATEST12322")
    # res = frog_model.edit_model(new_name="IKEATEST111")
    # print('res', res)

    # Delete Model
    # FrogModel.delete_model( model_name="IKEATEST111")

    # frog_model = FrogModel(app_key=app_key, model_name="IKEATEST111")
    # res = frog_model.delete()
    # print('res', res)

    # Share model
    # frog_model = FrogModel(app_key=app_key, model_name="IKEATEST")
    # res = frog_model.share(target_user="mr-cf-test-main")
    # print('res', res)
    
    # Remove Share access
    # frog_model = FrogModel(app_key=app_key, model_name="IKEATEST")
    # res = frog_model.remove_share_access(target_user="mr-cf-test-main")
    # print('res', res)

    # Clone model
    # frog_model = FrogModel(app_key=app_key, model_name="IKEATEST")
    # res = frog_model.clone("IKEATEST2")
    # print('res', res)

    # archive a model
    # frog_model = FrogModel(app_key=app_key, model_name="IKEATEST2")
    # res = frog_model.archive()
    # print(res)

    # archive restore
    # res = FrogModel.archive_restore(app_key=app_key, model_name="IKEATEST2")
    # print(res)

    # Get all archived models
    # res = FrogModel.archived_models(app_key=app_key)
    # print(res)

    ### Model management End

    # EXAMPLE: Scenario run

    # def run(
    #     self,
    #     scenarios: list[str] = ["Baseline"],
    #     wksp: str = "Studio",
    #     engine: None | ENGINES = None,
    #     run_neo_with_infeasibility: bool = False,
    #     resource_size: RESOURCE_SIZES = "s",
    #     tags: str = "",
    #     version: str = "",
    #     fire_and_forget: bool = False,
    #     correlation_id: str | None = None,
    #     check_configuration_before_run: bool = False
    # )

    # All scenarios within a model
    # scenarios = frog_model.all_scenarios_preview()
    # print(scenarios)

    # Run
    # run = frog_model.run_scenario() # just baseline
    # run = frog_model.run_scenario(['No Detroit DC', 'GF 9 Facilities', 'Throg Example', 'Hopper Example', 'No Flow Constraints', 'GF 10 Facilities'])
    # run = frog_model.run_scenario(['No Flow Constraints','GF 9 Facilities'], fire_and_forget=True)
    # print('scenarioRunFinished', run)

    # run = frog_model.run_scenario(['All'], check_configuration_before_run = True)
    # run = frog_model.run_scenario(['No Detroit DC'])
    # run = frog_model.run_scenario("No Detroit DC", fire_and_forget=True) # Run specific scenario
    # run = frog_model.run_scenario(["No Detroit DC"], engine="throg") # Run specific scenario with specific engine
    # run = frog_model.run_scenario(resource_size="4xs", fire_and_forget=True) # Run specific scenario with specific engine and resource size
    # print('scenarioRunFinished', run)

    # EXAMPLE Stop a scenario
    # frog_model = FrogModel(app_key=app_key, model_name="IKEATEST")
    # stop = frog_model.stop_scenario(scenario_name="Baseline")
    # stop = frog_model.stop_scenario(job_key="No Detroit DC")
    # print('stop', stop)

    # EXAMPLE Check scenario status
    # frog_model = FrogModel(app_key=app_key, model_name="IKEATEST")
    # status = frog_model.check_scenario_status(scenario_name="Baseline")
    # print('status', status)

    # status = frog_model.check_scenario_status(job_key="2ed63b69-907a-4c96-8efe-b9127041233f")
    # print('status', status)

    # EXAMPLE: check scenario logs
    # frog_model = FrogModel(app_key=app_key, model_name="IKEATEST")
    # logs = frog_model.get_job_logs(job_key="249c404d-2834-4e9c-8f56-f6e154aa2beb")
    # print('logs', logs)

    # EXAMPLE: MRO tables
    # frog_model = FrogModel(app_key=app_key, model_name="IKEATEST")
    # all_parameters = frog_model.get_all_run_parameters()
    # all_parameters = frog_model.get_all_run_parameters(engine="neo") # related to specific engine
    # print('all_parameters', all_parameters)

    # EXAMPLE: Want to update a parameter value before running the scenario
    # frog_model = FrogModel(app_key=app_key, model_name="IKEATEST")
    # update_run_parameter_value = frog_model.update_run_parameter_value("LaneCreationRule", "Transportation Policy Lanes Only")
    # update_run_parameter_value = frog_model.update_run_parameter_value("IKEATEST", "NumberOfReplications", "1")
    # print('update_run_parameter_value', update_run_parameter_value)

    # EXAMPLE: Want to create a new parameter
    # def add_run_parameter(self, model_name: str, model_run_option: ModelRunOption, correlation_id = None) -> dict:
    # res = frog_model.delete_run_parameter("bbb")
    # abc = frog_model.add_run_parameter( {"option": "bbb", "value": 'False', "datatype":"[True, False]"})
    # print('abc', abc)

    # EXAMPLE: Want to delete a parameter
    # def delete_run_parameter(self, model_name: str, parameter_name: str, correlation_id = None) -> dict:
    # res = frog_model.delete_run_parameter("bbb")
    # print('res', res)

    # EXAMPLE: Wait for geocode to finish
    # def geocode_table(
    #     self,
    #     table_name: str,
    #     geoprovider: str = "MapBox",
    #     geoapikey: str = None,
    #     ignore_low_confidence: bool = True,
    #     fire_and_forget: bool = True,
    # )
    # frog_model = FrogModel(app_key=app_key, model_name="IKEATEST")
    # abc = frog_model.geocode_table('facilities', fire_and_forget=False)
    # print('abc', abc)

    # Custom table/column CRUD
    # frog_model = FrogModel(app_key=app_key, model_name="IKEATEST")
    # frog_model = FrogModel(connection_string='postgresql://685ba205-712a-47af-81ad-9264d757f3ce_03415342db99:FByF11RmXw3PKMSH@685ba205-712a-47af-81ad-9264d757f3ce-0d1f55075408.database.optilogic.app:6432/685ba205-712a-47af-81ad-9264d757f3ce-0d1f55075408?sslmode=require&fallback_application_name=optilogic_sqlalchemy')

    # Create custom table
    table_name_var = "table_final"
    # delete = frog_model.delete_table(table_name_var)
    # print(delete)
    cde = frog_model.create_table(table_name_var)
    print(cde)
        #     table_name: str,
        # column_name: str,
        # data_type: str = "text",
        # key_column: bool = False,
        # pseudo: bool = True,
    # one_column = frog_model.create_custom_column(table_name_var, 'new_columnlala', 'integer', False, False)
    # print(one_column)
    # all custom tables
    # cde = frog_model.get_all_custom_tables()
    # print(cde)


    # delete custom table
    # cde = frog_model.delete_table("aaaaaab")
    # print(cde)

    # rename custom table
    # cde = frog_model.rename_table("ooooo", "eee")
    # print(cde)

    # create custom column
    # cde = frog_model.create_custom_column('newtable', 'new_column4', 'integer', True, False)
    # print(cde)

    bulk_cc = frog_model.bulk_create_custom_columns( [

                                                    {

                                                                              "table_name": table_name_var,

                                                                              "column_name": "CostTrace",

                                                                              "data_type": "text"

                                                    },

                                                    {

                                                                              "table_name": table_name_var,

                                                                              "column_name": "LaneStackability",

                                                                              "data_type": "text"

                                                    },

                                                    {

                                                                              "table_name": table_name_var,

                                                                              "column_name": "Pallets",

                                                                              "data_type": "text"

                                                    },

                                                    {

                                                                              "table_name": table_name_var,

                                                                              "column_name": "ScenarioFilters",

                                                                              "data_type": "text"

                                                    },

                                                    {

                                                                              "table_name": table_name_var,

                                                                              "column_name": "Shelflife",

                                                                              "data_type": "text"

                                                    },

                                                    {

                                                                              "table_name": table_name_var,

                                                                              "column_name": "Stackability",

                                                                              "data_type": "text"

                                                    },

                                                    {

                                                                              "table_name": table_name_var,

                                                                              "column_name": "StorageRequirement",

                                                                              "data_type": "text"

                                                    },

                                                    {

                                                                              "table_name": table_name_var,
                                                                              "column_name": "TransportationCost",
                                                                              "data_type": "text"

                                                    },

                                                    {

                                                                              "table_name": table_name_var,

                                                                              "column_name": "HandlingCost",

                                                                              "data_type": "text"

                                                    },

                                                    {

                                                                              "table_name": table_name_var,

                                                                              "column_name": "MTLTEXCLUSION",

                                                                              "data_type": "bool"

                                                    },

                                                    {

                                                                              "table_name": table_name_var,

                                                                              "column_name": "IsVMR",

                                                                              "data_type": "bool"

                                                    },

                                                    {

                                                                              "table_name": table_name_var,

                                                                              "column_name": "Transport_Cost_Rating",

                                                                              "data_type": "integer"

                                                    },

                                                    {

                                                                              "table_name": table_name_var,
                                                                              "column_name": "MR_Handling_Cost_Rating",
                                                                              "data_type": "integer"

                                                    },

                                                    {

                                                                              "table_name": table_name_var,

                                                                              "column_name": "Valid_SCND",

                                                                              "data_type": "bool"

                                                    },

                                                    {

                                                                              "table_name": table_name_var,

                                                                              "column_name": "Transport_Time_Num",

                                                                              "data_type": "numeric"

                                                    },

                                                    {

                                                                              "table_name": table_name_var,

                                                                              "column_name": "Destination_Transport_Zone",

                                                                              "data_type": "text"

                                                    }

                          ])

    print(bulk_cc)

    # update custom column
    # def edit_custom_column(self, table_name: str, column_name: str, new_column_name: str = None, data_type: str = None, key_column: bool = None):
    # cde = frog_model.edit_custom_column('newtable', 'new_column4', data_type='text', key_column=False)
    # print(cde)

    # delete custom column
    # cde = frog_model.delete_custom_column('newtable', 'new_column4')
    # print(cde)


    # all custom columns
    # cde = frog_model.get_all_custom_columns('newtable')
    # print(cde)

if __name__ == "__main__":
    main()
