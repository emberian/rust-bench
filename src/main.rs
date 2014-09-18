extern crate membench;
extern crate serialize;

#[deriving(Encodable, Decodable)]
struct Output{
    cli: String,
    memory_data: Vec<(f64, u64)>,
    cpuacct: membench::CpuacctStats
}

fn main() {
    let args = std::os::args();

    let stats = membench::measure_cmd(args[1].as_slice(), args.as_slice().slice_from(2));
    let enc = serialize::json::encode(&stats);
    println!("{}", enc);
}
