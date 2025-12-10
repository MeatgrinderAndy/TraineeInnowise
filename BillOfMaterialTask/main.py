import pandas as pd
from configparser import ConfigParser

def process_bom_hierarchy(data):
    
    group_cols = [
        'year', 'plant_id', 
        'produced_material', 'produced_material_production_type', 'produced_material_release_type',
        'component_material', 'component_material_production_type', 'component_material_release_type'
    ]
    
    df_agg = data.groupby(group_cols, dropna=False)[['produced_material_quantity', 'component_material_quantity']].sum().reset_index()
    
    final_rows = []

    contexts = df_agg[['year', 'plant_id']].drop_duplicates()
    
    for i, ctx in contexts.iterrows():
        year = ctx['year']
        plant = ctx['plant_id']
        
        ctx_df = df_agg[(df_agg['year'] == year) & (df_agg['plant_id'] == plant)]
        
        adj = {}
        for j, row in ctx_df.iterrows():
            parent = row['produced_material']
            if parent not in adj:
                adj[parent] = []
            adj[parent].append(row)
            
        roots = ctx_df[ctx_df['produced_material_release_type'] == 'FIN']['produced_material'].unique()
        
        for root_id in roots:
            root_edges = adj.get(root_id, [])
            
            for root_edge in root_edges:
                fin_attrs = {
                    'plant': plant,
                    'year': year,
                    'fin_material_id': root_edge['produced_material'],
                    'fin_material_release_type': root_edge['produced_material_release_type'],
                    'fin_material_production_type': root_edge['produced_material_production_type'],
                    'fin_production_quantity': root_edge['produced_material_quantity']
                }
                
                stack = [(root_edge, fin_attrs)]
                
                while stack:
                    curr_edge, curr_fin_attrs = stack.pop()
                    row_data = curr_fin_attrs.copy()
                    row_data.update({
                        'prod_material_id': curr_edge['produced_material'],
                        'prod_material_release_type': curr_edge['produced_material_release_type'],
                        'prod_material_production_type': curr_edge['produced_material_production_type'],
                        'prod_material_production_quantity': curr_edge['produced_material_quantity'],
                        
                        'component_id': curr_edge['component_material'],
                        'component_material_release_type': curr_edge['component_material_release_type'],
                        'component_material_production_type': curr_edge['component_material_production_type'],
                        'component_consumption_quantity': curr_edge['component_material_quantity']
                    })
                    
                    final_rows.append(row_data)
                    child_id = curr_edge['component_material']
                    if child_id in adj:
                        children_edges = adj[child_id]
                        for child_edge in children_edges:
                            stack.append((child_edge, curr_fin_attrs))

    result_df = pd.DataFrame(final_rows)
    
    ordered_cols = [
        'plant',
        'fin_material_id',
        'fin_material_release_type',
        'fin_material_production_type',
        'fin_production_quantity',
        'prod_material_id',
        'prod_material_release_type',
        'prod_material_production_type',
        'prod_material_production_quantity',
        'component_id',
        'component_material_release_type',
        'component_material_production_type',
        'component_consumption_quantity',
        'year'
    ]
    
    for col in ordered_cols:
        if col not in result_df.columns:
            result_df[col] = None
            
    result_data = result_df[ordered_cols]
    
    return result_data

config = ConfigParser()
config.read('.config')

data = pd.read_excel(config['FILE_PATHS']['INPUT_FILE'])

result_data = process_bom_hierarchy(data)

result_data.to_excel(config['FILE_PATHS']['OUTPUT_FILE'], index=False)