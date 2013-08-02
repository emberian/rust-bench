/*!
 * A node whose job is to start and finish builds.
 */

extern mod zmq;
use std::rt::io::mem::{MemReader, MemWriter};
use std::rt::io::*;
use std::rt::io::extensions::*;

#[deriving(Clone, IterBytes)]
struct Job {
    /// Job ID, used for stuff.
    id: u64,
    /// Commit ID (SHA1 sum)
    commit: ~str,
    /// Configure arguments
    configure: ~str,
    /// Make arguments
    make: ~str,
}

fn main() {
    let context = zmq::Context::new();
    let server = context.socket(zmq::REQ).unwrap();
    server.connect("tcp://localhost:7539");

    loop {
        let mut msg = MemWriter::new();
        msg.write(bytes!(0));
        server.send(msg.buf, 0);

        let msg = MemReader::new(server.recv_bytes(0).unwrap());
        printfln!("%?", msg);
        unsafe { std::libc::sleep(5) };
    }
}
