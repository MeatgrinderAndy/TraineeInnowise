CREATE TABLE IF NOT EXISTS bill_of_material_data (
    year INTEGER,
    month INTEGER,
    produced_material VARCHAR(10),
    produced_material_production_type VARCHAR(10),
    produced_material_release_type VARCHAR(10),
    produced_material_quantity NUMERIC(20, 2) DEFAULT 0,
    component_material VARCHAR(10),
    component_material_production_type VARCHAR(10),
    component_material_release_type VARCHAR(10),
    component_material_quantity NUMERIC(20, 2) DEFAULT 0,
    plant_id VARCHAR(50)
);

CREATE INDEX IF NOT EXISTS idx_bom_plant_year ON bill_of_material_data(plant_id, year, month);

CREATE TABLE IF NOT EXISTS bom_result (
    plant VARCHAR(50),
    fin_material_id VARCHAR(10),
    fin_material_release_type VARCHAR(10),
    fin_material_production_type VARCHAR(10),
    fin_production_quantity NUMERIC,
    prod_material_id VARCHAR(10),
    prod_material_release_type VARCHAR(10),
    prod_material_production_type VARCHAR(10),
    prod_material_production_quantity NUMERIC,
    component_id VARCHAR(10),
    component_material_release_type VARCHAR(10),
    component_material_production_type VARCHAR(10),
    component_consumption_quantity NUMERIC,
    year INTEGER
);

