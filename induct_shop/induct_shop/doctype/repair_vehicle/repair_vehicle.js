// Copyright (c) 2026, Induct and contributors
// For license information, please see license.txt

const _F='Tesla Fremont, CA',_SH='Giga Shanghai, China',_LFP='LFP — Lithium Iron Phosphate Battery',_ELI='Electric — Lithium-Ion';
const _MB='Manual belts + Front Airbags',_OD=', Occupant Detection',_SI=', Side Inflatable Restraints',_KA=', Knee Airbags',_AH=' + Active Hood';
const _R5 =_MB+_OD+_SI+_KA+' — 5-seat';
const _R5s=_MB+_SI+' — 5-seat';
const _R7 =_MB+_OD+_SI+_KA+' — 7-seat (2+3+2)';
const _R6 =_MB+_OD+_SI+_KA+' — 6-seat (2+2+2)';
const _R5c=_MB+_OD+_SI+' — 5-seat (2+3)';
const _R5d=_MB+_OD+_SI+_KA+' — 5-seat (2+3)';
const _RAH=_MB+_SI+_AH+' — 5-seat';

const _SB12={A:'Hatchback 5-Door LHD — RWD',B:'Hatchback 5-Door LHD — AWD',C:'Hatchback 5-Door RHD — RWD',D:'Hatchback 5-Door RHD — AWD'};
const _SF12={A:'10 kW Charger',B:'20 kW Charger',C:'10 kW Charger + DC Fast Charge',D:'20 kW Charger + DC Fast Charge'};
const _SD12={C:'Base AC Motor — Tier 2 Battery (31–40 kWh)',G:'Base AC Motor — Tier 4 Battery (51–60 kWh)',N:'Base AC Motor — Tier 7 Battery (81–90 kWh)',P:'Performance AC Motor — Tier 7 Battery (81–90 kWh)'};
const _SD1518={1:'Single Motor — Large Base',2:'Dual Motor — Small Base + Small Base',3:'Single Motor — Large Performance',4:'Dual Motor — Small Base + Large Performance'};
const _SD1920={1:'Single Motor — Standard',2:'Dual Motor — Standard',3:'Single Motor — Performance',4:'Dual Motor — Performance'};
const _SR12  ={1:'USA manual belts + front airbags, front/rear side airbags, knee airbags — 5-seat',2:'EU manual belts + front airbags, front/rear side airbags, knee airbags — 5-seat'};
const _SR1517={1:_R5,3:_R5s,7:_RAH};
const _SR1820={1:_R5,3:_R5s,7:_R5s};
const _SLE={E:'Electric'};

const MODEL={S:'Model S',3:'Model 3',X:'Model X',Y:'Model Y',C:'Cybertruck',R:'Roadster',A:'Cybercab',T:'Semi'};
const ALL_WMI=new Set(['5YJ','7SA','LRW','XP7','SFZ','5XJ','3MW','7G2']);

const WMI={
  3:{'5YJ':_F+' / Austin, TX','5XJ':_F+' (Secondary)',LRW:_SH,'3MW':'Monterrey, Mexico (Future)'},
  S:{'5YJ':_F,'5XJ':_F+' (Secondary)'},
  X:{'7SA':_F+' / Austin, TX'},
  Y:{'5YJ':'Tesla Fremont — through Model Year 2021','7SA':'Tesla Fremont / Giga Texas — from Model Year 2022',LRW:_SH,XP7:'Giga Berlin, Germany','3MW':'Monterrey, Mexico (Future)'},
  C:{'5YJ':_F,'7SA':'Tesla Austin, TX','7G2':'Tesla Austin, TX / Giga Nevada'},
  R:{SFZ:'Lotus Factory — Norfolk, UK'},
  A:{'5YJ':_F},
  T:{'7G2':'Tesla Austin, TX / Giga Nevada'},
};

const BODY={
  3:{E:'Sedan 4-Door — Left-Hand Drive',F:'Sedan 4-Door — Right-Hand Drive'},
  S:{A:'Hatchback 5-Door — Left-Hand Drive',B:'Hatchback 5-Door — Right-Hand Drive'},
  X:{C:'Class E MPV 5-Door — Left-Hand Drive',D:'Class E MPV 5-Door — Right-Hand Drive'},
  Y:{G:'Class D MPV 5-Door — Left-Hand Drive',H:'Class D MPV 5-Door — Right-Hand Drive'},
  C:{E:'Truck / Pickup — Left-Hand Drive',J:'Crew Cab — Left-Hand Drive'},
  A:{J:'Robotaxi Body'},
  T:{K:'Day Cab — No Sleeper',L:'Sleeper Cab — With Sleeper Berth',1:'Day Cab — Standard'},
};

const RESTRAINT={
  3:{1:_R5,7:_R5s},
  S:{1:_R5,7:_R5s},
  X:{A:_R7,B:_R6,C:_R5c,D:_R5d},
  Y:{A:_R7,B:_R6,C:_R5c,D:_R5d},
  C:{H:_R5,G:'Class 2B-3 GVWR (8,501–14,000 lbs)',B:'Class 2B GVWR'},
  R:{2:'Manual Seatbelts'},
  A:{E:'Robotaxi Restraint System'},
  T:{H:'Class 8 GVWR (Over 33,000 lbs)',E:'Class 8 GVWR (33,001+ lbs)'},
};

const FUEL={
  3:{E:'Electric — Li-ion NMC/NCA Battery',F:_LFP,H:_LFP},
  S:{E:'Electric'},
  X:{E:'Electric'},
  Y:{E:'Electric — Li-ion NMC/NCA Battery',F:_LFP,H:_LFP},
  C:{S:'Standard Range (~250 mi)',R:'Long Range (~340 mi)',E:_ELI,0:'Battery — Base'},
  R:{B:'Battery — Lithium-Ion'},
  A:{E:_ELI},
  T:{S:'Standard Range (~300 mi)',R:'Long Range (~500 mi)',E:_ELI,0:'Battery — Base'},
};

const DRIVE={
  3:{A:'Single Motor — Standard (3DU 800A)',B:'Dual Motor — Standard',C:'Dual Motor — Performance',J:'Single Motor — Hairpin Winding',K:'Dual Motor — Hairpin Winding',L:'Dual Motor — Hairpin Winding Performance',R:'Single Motor — Standard (3DU 600A)',S:'Single Motor — Standard (DUB 600A)',T:'Dual Motor — Performance (Highland)'},
  S:{5:'Dual Motor',6:'Triple Motor — Plaid'},
  X:{5:'Dual Motor',6:'Triple Motor — Plaid'},
  Y:{D:'Single Motor — Standard',E:'Dual Motor — Standard',F:'Dual Motor — Performance (3DU 800A)',J:'Single Motor — Hairpin Winding',K:'Dual Motor — Hairpin Winding',L:'Dual Motor — Hairpin Winding Performance',R:'Single Motor — Standard (3DU 600A)',S:'Single Motor — Standard (DUB 600A)'},
  C:{D:'Dual Motor — AWD Standard',E:'Triple Motor — Cyberbeast Performance'},
  R:{4:'Single Motor — AC Induction'},
  A:{U:'Robotaxi Drive Unit'},
  T:{B:'Dual Drive Rear Axle — Air Brakes',0:'Drive Unit — Standard'},
};

const YEAR={8:'2008',9:'2009',A:'2010',B:'2011',C:'2012',D:'2013',E:'2014',F:'2015',G:'2016',H:'2017',J:'2018',K:'2019',L:'2020',M:'2021',N:'2022',P:'2023',R:'2024',S:'2025',T:'2026',V:'2027'};

const PLANT={F:'Tesla Factory — Fremont, CA',A:'Giga Texas — Austin, TX',C:'Giga Shanghai — China',B:'Giga Berlin — Germany',G:'Giga Berlin — Brandenburg, Germany',N:'Giga Nevada — Reno, NV',1:'Lotus Factory — Norfolk, UK',3:'Palo Alto — R&D / Prototypes',P:'Palo Alto — R&D / Prototypes'};

const S_LEGACY_YEARS=new Set(['C','D','E','F','G','H','J','K','L']);
const S_LEGACY={
  body:{C:_SB12,D:_SB12},
  restraint:{
    C:_SR12,D:_SR12,
    E:{1:_R5,2:_MB+_SI+_KA+' — 5-seat',4:_MB+_SI+_KA+' — 4-seat (2+2)',5:_MB+_SI+' — 4-seat (2+2)',6:_MB+_SI+' — 5-seat',7:_RAH,8:_MB+_SI+_AH+' — 4-seat (2+2)'},
    F:{1:_R5,3:_R5s,6:_R5s,7:_RAH,8:_MB+_SI+_AH+' — 4-seat (2+2)'},
    G:_SR1517,H:_SR1517,
    J:_SR1820,K:_SR1820,L:_SR1820,
  },
  fuel:{
    C:_SF12,D:_SF12,
    E:{H:'Li-ion — High Capacity',S:'Li-ion — Standard Capacity'},
    F:{S:'Li-ion — Standard Capacity',H:'Li-ion — High Capacity',V:'Li-ion — Ultra High Capacity',E:'Electric'},
    G:_SLE,H:_SLE,J:_SLE,K:_SLE,L:_SLE,
  },
  drive:{
    C:_SD12,D:_SD12,
    E:{1:'Single Motor — 3-Phase AC Induction',2:'Dual Motor — 3-Phase AC Induction'},
    F:_SD1518,G:_SD1518,H:_SD1518,J:_SD1518,
    K:_SD1920,L:_SD1920,
  },
  typedSeq:new Set(['C','D','E']),
};

function getHW(m,seq,plant,yr){
  const year=parseInt(YEAR[yr]||0);
  if(m==='C'||m==='A'||m==='T')return{t:'HW4'};
  if(m==='Y'){
    if(year>=2024)return{t:'HW4'};
    if(plant==='F'){
      if(seq>=800000)return{t:'Likely HW4'};
      if(seq>=790000)return{t:'Possibly HW4'};
    }else if(plant==='A'){
      if(seq>=131200)return{t:'Likely HW4'};
      if(seq>=127000)return{t:'Possibly HW4'};
    }else{
      if(year===2023)return{t:'Possibly HW4'};
    }
    if(year===2023)return{t:'Possibly HW4'};
    return{t:'Shipped with HW3'};
  }
  if(m==='X'){
    if(seq>=385000)return{t:'Likely HW4'};
    if(seq>=370000)return{t:'Possibly HW4'};
    if(year>=2020&&year<=2022)return{t:'Shipped with HW3'};
    if(year===2019)return{t:'HW2.5 or HW3'};
    if(year===2018)return{t:'Shipped with HW2.5'};
    if(year===2017)return{t:'HW2.0 or HW2.5'};
    if(year===2016)return{t:'HW1 or HW2.0'};
    if(year===2015)return{t:'Shipped with HW1'};
    return null;
  }
  if(m==='S'){
    if(!S_LEGACY_YEARS.has(yr)){
      if(seq>=502000)return{t:'Likely HW4'};
      if(seq>=501000)return{t:'Possibly HW4'};
      return{t:'Shipped with HW3'};
    }
    if(year===2020)return{t:'Shipped with HW3'};
    if(year===2019)return{t:'HW2.5 or HW3'};
    if(year===2018)return{t:'Shipped with HW2.5'};
    if(year===2017)return{t:'HW2.0 or HW2.5'};
    if(year===2016)return{t:'HW1 or HW2.0'};
    if(year===2015)return{t:'Shipped with HW1'};
    if(year===2014)return{t:'No AP or HW1'};
    if(year<=2013)return{t:'No autopilot hardware'};
    return null;
  }
  if(m==='3'){
    if(year>=2024)return{t:'HW4'};
    if(year===2023)return{t:'Possibly HW4'};
    if(year>=2020&&year<=2022)return{t:'Shipped with HW3'};
    if(year===2019)return{t:'HW2.5 or HW3'};
    if(year===2017||year===2018)return{t:'Shipped with HW2.5'};
    return null;
  }
  return null;
}

function getDerived(m,driveCode,restraintCode,bodyCode,plant,yr,isLS){
  const year=parseInt(YEAR[yr]||0);
  let drivetrain=null;
  if(m==='R') drivetrain='RWD';
  else if(m==='T'||m==='A') drivetrain=null;
  else if(isLS){
    drivetrain=year<=2013?'RWD':['2','4'].includes(driveCode)?'AWD':'RWD';
  } else {
    const AWD={S:['5','6'],3:['B','C','K','L','T'],X:['5','6'],Y:['E','F','K','L'],C:['D','E']};
    if(driveCode) drivetrain=(AWD[m]||[]).includes(driveCode)?'AWD':'RWD';
  }
  let trim=null;
  if(isLS){
    if(['C','G','N','P'].includes(driveCode)){
      trim={C:'40 kWh',G:'60 kWh',N:'85 kWh',P:'P85 Performance'}[driveCode];
    } else if(year<=2014){
      trim=driveCode==='2'?'Dual Motor':'Standard';
    } else if(year<=2018){
      trim={'1':'Standard','2':'Dual Motor','3':'Performance','4':'Dual Motor Performance'}[driveCode]||null;
    } else {
      trim={'1':'Standard Range','2':'Long Range','3':'Performance','4':'Long Range Performance'}[driveCode]||null;
    }
  } else {
    trim=({
      S:{'5':'Long Range','6':'Plaid'},
      3:{'A':'Standard Range','B':'Long Range','C':'Performance','J':'Standard Range','K':'Long Range','L':'Performance','R':'Standard Range','S':'Standard Range','T':'Performance'},
      X:{'5':'Long Range','6':'Plaid'},
      Y:{'D':'Standard Range','E':'Long Range','F':'Performance','J':'Standard Range','K':'Long Range','L':'Performance','R':'Standard Range','S':'Standard Range'},
      C:{'D':'Dual Motor','E':'Cyberbeast'},
      R:{'4':'Sport'},
      T:{'B':'Semi'},
    }[m]||{})[driveCode]||null;
  }
  return{drivetrain,trim};
}

function chk(v){
  const xl={A:1,B:2,C:3,D:4,E:5,F:6,G:7,H:8,J:1,K:2,L:3,M:4,N:5,P:7,R:9,S:2,T:3,U:4,V:5,W:6,X:7,Y:8,Z:9};
  const w=[8,7,6,5,4,3,2,10,0,9,8,7,6,5,4,3,2];
  let s=0;
  for(let i=0;i<17;i++){
    const c=v[i];
    if (!xl[c] && !(c>='0'&&c<='9')) return '?';
    s+=(c>='0'&&c<='9'?+c:xl[c])*w[i];
  }
  const r=s%11;return r===10?'X':''+r;
}

frappe.ui.form.on("Repair Vehicle", {
	vin: function(frm) {
        let raw = frm.doc.vin || "";
        let v = raw.toUpperCase().replace(/[^A-HJ-NPR-Z0-9]/g, '');
        
        if (raw !== v) {
            frm.set_value('vin', v);
        }
        
        if (v.length === 17) {
            let wmi = v.slice(0, 3);
            if (!ALL_WMI.has(wmi)) {
                frappe.msgprint(`"${wmi}" is not a recognized Tesla manufacturer code.`);
                frm.set_value('is_valid_vin', 0);
                return;
            }
            
            let exp = chk(v);
            let got = v[8];
            frm.set_value('is_valid_vin', got === exp ? 1 : 0);
            
            let m = v[3];
            let yr = v[9];
            let isLS = m === 'S' && S_LEGACY_YEARS.has(yr);
            
            let manufacturer = (WMI[m] || {})[wmi] || "Tesla";
            let bm = isLS ? (S_LEGACY.body[yr] || BODY.S) : (BODY[m] || {});
            let fm = isLS ? (S_LEGACY.fuel[yr] || {}) : (FUEL[m] || {});
            let dm = isLS ? (S_LEGACY.drive[yr] || {}) : (DRIVE[m] || {});
            
            let tc = v[11];
            let seq = isLS && S_LEGACY.typedSeq.has(yr) ? v.slice(12) : v.slice(11);
            let seqNum = parseInt(seq, 10);
            
            let hw = getHW(m, seqNum, v[10], yr);
            let d = getDerived(m, v[7], v[5], v[4], v[10], yr, isLS);
            
            frm.set_value('manufacturer', manufacturer);
            frm.set_value('model', MODEL[m] || "Unknown");
            frm.set_value('model_year', YEAR[yr] || yr);
            frm.set_value('body_type', bm[v[4]] || "Unknown");
            frm.set_value('trim', d.trim || "Unknown");
            frm.set_value('drivetrain', d.drivetrain || "Unknown");
            frm.set_value('battery_type', fm[v[6]] || "Unknown");
            frm.set_value('drive_unit', dm[v[7]] || "Unknown");
            frm.set_value('assembly_plant', PLANT[v[10]] || v[10]);
            frm.set_value('production_sequence', seq);
            frm.set_value('autopilot_hardware', hw ? hw.t : "Unknown");
        } else {
            // clear fields if not 17 chars
            ['is_valid_vin', 'manufacturer', 'model', 'model_year', 'body_type', 'trim', 'drivetrain', 'battery_type', 'drive_unit', 'assembly_plant', 'production_sequence', 'autopilot_hardware'].forEach(f => {
                frm.set_value(f, '');
            });
        }
	}
});
