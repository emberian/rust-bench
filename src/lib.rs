#![feature(phase)]
extern crate cgroup;
extern crate time;
extern crate regex;
#[phase(plugin)] extern crate regex_macros;
extern crate libc;
extern crate serialize;

use std::io::Command;
use time::precise_time_ns as t;

#[deriving(Encodable, Decodable)]
pub struct CpuacctStats {
    pub hz: f64,
    pub user: f64,
    pub system: f64,
    pub usage: f64
}

#[deriving(Encodable, Decodable)]
pub struct CommandStats {
    pub elapsed: u64,
    pub memory_data: Vec<(f64, u64)>,
    pub max_memory: u64,
    pub cpuacct: CpuacctStats,
    pub stdout: String,
    pub stderr: String,
}

pub fn process_stat(mstat: &str) -> u64 {
    let re = regex!("^(total_cache|total_rss|total_swap)$");

    let mut tot = 0u64;

    for line in mstat.lines() {
        if line.len() == 0 {
            break
        }

        let mut spl = line.split(' ');
        let k = spl.next().unwrap();
        let v = spl.next().unwrap();

        if re.is_match(k) {
            tot += from_str(v).unwrap();
        }
    }

    tot
}

pub fn measure_cmd(prog: &str, args: &[String]) -> CommandStats {
    let mut sdr = Command::new("systemd-run");
    sdr.args(&["-p", "MemoryAccounting=Yes", "--user", "--scope"]);
    sdr.arg(prog);
    sdr.args(args);

    println!("{}", sdr.to_string());

    let start = t();

    let mut prc = sdr.spawn().unwrap();
    let pid = prc.id();

    println!("Child process: {}", pid);

    let cgr = cgroup::CGroup::from_base_and_pid(Path::new("/sys/fs/cgroup"), pid).unwrap();
    let mem = cgr.controller(b"memory").expect("No memory :(");
    let cpu = cgr.controller(b"cpu,cpuacct").expect("No cpu,cpuacct :(");

    let mut data: Vec<(f64, u64)> = Vec::new();

    while prc.signal(0).is_ok() {
        let t_ = t();
        let mst = mem.get(b"memory.stat").expect("No memory.stat :(").unwrap();
        let memuse = process_stat(mst.as_slice());
        if memuse != (*data.last().unwrap_or(&(0., 0))).val1() {
            data.push(((t_ - start) as f64 / 1_000_000_000.0, memuse));
        }
    }

    let elapsed = t() - start;
    let max_memory = from_str(mem.get(b"memory.max_usage_in_bytes").expect("No max_usage_in_bytes :(").unwrap().as_slice().trim()).expect("max_usage_in_bytes derped");
    let cau = cpu.get(b"cpuacct.usage").unwrap().unwrap();
    let cas = cpu.get(b"cpuacct.stat").unwrap().unwrap();
    let mut cas = cas.as_slice().lines();

    let user_hz = 1.0 /
        unsafe {
            libc::sysconf(libc::consts::os::sysconf::_SC_CLK_TCK) as f64
        };

    let cpuacct = CpuacctStats {
        hz: user_hz,
        user: from_str::<f64>(cas.next().unwrap().slice_from(5).trim()).unwrap() * user_hz,
        system: from_str::<f64>(cas.next().unwrap().slice_from(7).trim()).unwrap() * user_hz,
        usage: from_str(cau.as_slice().trim()).unwrap(),
    };

    let output = prc.wait_with_output().unwrap();

    let stdout = String::from_utf8(output.output).unwrap();
    let stderr = String::from_utf8(output.error).unwrap();

    CommandStats {
        elapsed: elapsed,
        memory_data: data,
        max_memory: max_memory,
        cpuacct: cpuacct,
        stdout: stdout,
        stderr: stderr
    }
}
