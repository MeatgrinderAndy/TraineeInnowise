CREATE OR REPLACE PROCEDURE process_bom_hierarchy()
LANGUAGE plpgsql
AS $$
BEGIN
    TRUNCATE TABLE bom_result;
    
    INSERT INTO bom_result (
        plant, 
        fin_material_id, fin_material_release_type, fin_material_production_type, fin_production_quantity,
        prod_material_id, prod_material_release_type, prod_material_production_type, prod_material_production_quantity,
        component_id, component_material_release_type, component_material_production_type, component_consumption_quantity,
        year
    )
    WITH RECURSIVE 
    agg_data AS (
        SELECT 
            year, 
            plant_id,
            produced_material,
            produced_material_production_type,
            produced_material_release_type,
            component_material,
            component_material_production_type,
            component_material_release_type,
            SUM(produced_material_quantity) as prod_qty,
            SUM(component_material_quantity) as comp_qty
        FROM bill_of_material_data
        GROUP BY 
            year, plant_id, 
            produced_material, produced_material_production_type, produced_material_release_type,
            component_material, component_material_production_type, component_material_release_type
    ),
    bom_tree (
        plant_id,
        fin_material_id, fin_material_release_type, fin_material_production_type, fin_production_quantity,
        prod_material_id, prod_material_release_type, prod_material_production_type, prod_material_production_quantity,
        component_id, component_material_release_type, component_material_production_type, component_consumption_quantity,
        year,
        sort_path
    ) AS (
        SELECT 
            t.plant_id,
            t.produced_material,                   
            t.produced_material_release_type,       
            t.produced_material_production_type,    
            t.prod_qty,                             
            t.produced_material,                    
            t.produced_material_release_type,       
            t.produced_material_production_type,    
            t.prod_qty,                             
            t.component_material,                   
            t.component_material_release_type,      
            t.component_material_production_type,   
            t.comp_qty,                             
            t.year,
            ARRAY[t.plant_id::text, t.year::text, t.produced_material::text, t.component_material::text]
        FROM agg_data t
        WHERE t.produced_material_release_type = 'FIN' 

        UNION ALL

        SELECT 
            parent.plant_id,
            parent.fin_material_id,                 
            parent.fin_material_release_type,       
            parent.fin_material_production_type,    
            parent.fin_production_quantity,         
            child.produced_material,
            child.produced_material_release_type,
            child.produced_material_production_type,
            child.prod_qty,
            child.component_material,
            child.component_material_release_type,
            child.component_material_production_type,
            child.comp_qty,
            parent.year,
            parent.sort_path || child.component_material::text
        FROM agg_data child
        INNER JOIN bom_tree parent 
            ON parent.component_id = child.produced_material
            AND parent.plant_id = child.plant_id
            AND parent.year = child.year
    )
    SELECT 
        plant_id,
        fin_material_id, fin_material_release_type, fin_material_production_type, fin_production_quantity,
        prod_material_id, prod_material_release_type, prod_material_production_type, prod_material_production_quantity,
        component_id, component_material_release_type, component_material_production_type, component_consumption_quantity,
        year
    FROM bom_tree
    ORDER BY sort_path; 
END;
$$;

call process_bom_hierarchy()

