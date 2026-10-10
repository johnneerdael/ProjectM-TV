//! Official Naga parse/validate/serialize APIs; no custom instruction parser.
use std::{env, fs};

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() == 2 && args[1] == "--version" {
        println!("source-shader-naga-worker/1 naga30.0.0 wgpu14dd4e8f717cd8c4381908895495ea19ef924c35");
        return;
    }
    let result = inspect(args.get(1).map(String::as_str));
    println!("{}", result.unwrap_or_else(|reason| serde_json::json!({"status":"unsupported","reason":reason})));
}

fn inspect(path: Option<&str>) -> Result<serde_json::Value, String> {
    let path = path.ok_or("inspection SPIR-V input required")?;
    let size = fs::metadata(path).map_err(|e| e.to_string())?.len();
    if size > 8_000_000 { return Err("inspection module exceeds byte budget".into()); }
    let bytes = fs::read(path).map_err(|e| e.to_string())?;
    let module = naga::front::spv::parse_u8_slice(&bytes, &naga::front::spv::Options::default())
        .map_err(|e| format!("SPIR-V frontend: {e:?}"))?;
    let info = naga::valid::Validator::new(naga::valid::ValidationFlags::all(), naga::valid::Capabilities::all())
        .validate(&module).map_err(|e| format!("full inspection validation: {e:?}"))?;
    let functions: Vec<_> = module.functions.iter().map(|(handle, function)| {
        serde_json::json!({"name":function.name,"info":&info[handle]})
    }).collect();
    let entries: Vec<_> = module.entry_points.iter().enumerate().map(|(index, entry)| {
        serde_json::json!({"name":entry.name,"info":info.get_entry_point(index)})
    }).collect();
    Ok(serde_json::json!({"schema_version":1,"status":"validated_inspection_ir",
        "validation_flags":"all","capabilities":"all; inspection only",
        "functions":functions,"entries":entries,"module":module,
        "native_numeric_equivalence_verified":false,"runtime_texture_bindings_verified":false}))
}
