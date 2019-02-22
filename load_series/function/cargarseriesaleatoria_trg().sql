-- Function: cargarseriesaleatoria_trg()

-- DROP FUNCTION cargarseriesaleatoria_trg();

CREATE OR REPLACE FUNCTION cargarseriesaleatoria_trg()
  RETURNS trigger AS
$BODY$ DECLARE 
v_tmplid integer;
v_producto  integer;
v_lote integer;
v_location integer;
v_RECORD RECORD;
cont integer;
v_productoname character varying(100);
v_cont integer;
v_total integer;
v_total2 integer;
v_contpr integer;
v_locationid integer;
v_qtydone numeric;
v_qty double precision;
v_origin character varying(67);
v_order integer;
v_price numeric;
v_serie  character varying(67);
v_seriemax  character varying(67);
v_consecutivo character varying(67);
v_prefijo numeric;
v_id integer;
--cantidad double;
cur_id RECORD;
cur_as RECORD;
conta integer;
v_track character varying(20);
BEGIN
--raise exception '%','valor ';
for cur_id in (select id,location_id,product_qty, product_id
			from stock_pack_operation where picking_id=new.stockpicking_id ) 
loop
     Select product_tmpl_id into v_tmplid FROM product_product where id=cur_id.product_id;
     select tracking into v_track from product_template where id=v_tmplid;
     --raise exception '%','valor '|| v_track;
    IF v_track ='lot' OR v_track = 'serial' THEN
conta:=1;
	while(conta <= cur_id.product_qty ) 
	loop
		Select count(id) into cont from stock_pack_operation_lot where lot_name like '%al%';
		
		IF cont = 0 THEN 
		--RAISE EXCEPTION '%','ENTRO';
			v_serie := 'al1';
		--RAISE EXCEPTION '%','ENTRO';	
		ELSE  
		--RAISE EXCEPTION '%','ENTRO1';	
		--Select  max(id) from stock_production_lot where name like '%m%' order by  id asc;
			Select max(id) into  v_id from stock_pack_operation_lot where lot_name like '%al%';
			select substring(lot_name from 3 ) into v_consecutivo from stock_pack_operation_lot where id=v_id;
			v_prefijo := v_consecutivo::integer+1;
			v_serie:= 'al' || v_prefijo::text;
		END IF;
		
		/*
			INSERT INTO stock_production_lot(
				     product_id,  name,load)
			    VALUES (cur_id.product_id, v_serie,'t');
			  */  
			SELECT id into v_lote from stock_production_lot where  product_id=cur_id.product_id and name=v_serie;
			v_qty := v_qtydone::double precision;
	
			select origin into v_origin from stock_picking where id=new.stockpicking_id;
			SELECT id into v_order FROM purchase_order where name=v_origin;
			select price_unit into v_price from purchase_order_line where order_id=v_order and product_id=cur_id.product_id;
			/*
			INSERT INTO stock_quant(
				     lot_id, location_id, company_id,qty, product_id, in_date,create_date,create_uid,write_uid,write_date
				     ,cost)
			    VALUES (v_lote, cur_id.location_id, 1,1, cur_id.product_id, now(),NOW(),1,1,NOW(),v_price);
			*/
			--Raise exception '%','lote '||v_serie;
			INSERT INTO stock_pack_operation_lot(
					    lot_name, qty_todo, qty, 
					     operation_id,create_date,create_uid,write_uid,write_date)
				    VALUES (v_serie, 0, 1, cur_id.id,NOW(),1,1,NOW());

				
			
			Select count(*) into v_total from stock_pack_operation_lot  where operation_id=cur_id.id;
			Update stock_pack_operation set qty_done=v_total::numeric  where id=cur_id.id;
			conta:=conta+1;

	END loop;
   END IF;	
END loop;

 RETURN NEW;
END 

; $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION cargarseriesaleatoria_trg()
  OWNER TO postgres;


  CREATE TRIGGER cargarseriesaleatoria_trg
  BEFORE INSERT OR UPDATE
  ON series_aleatorias
  FOR EACH ROW
  EXECUTE PROCEDURE cargarseriesaleatoria_trg();
