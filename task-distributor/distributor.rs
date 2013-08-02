/*!
 * A node which does the administration of worker jobs. It decides which
 * commits are to be built, creates a Job, and sends it to the first client
 * which asks for a Job to execute. After 30 minutes of not receiving a
 * response for a job, it will use a PUB to ask if any clients are actively
 * working on the job, and if not, will reschedule it. It expects a response
 * on the normal REP socket.
 */

extern mod extra;
extern mod zmq;

use extra::time;
use extra::time::Timespec;

use std::to_bytes::ToBytes;
use std::hashmap::HashMap;
use std::rt::io::mem::MemReader;
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
    /// Timestamp from the last time we heard about this Job
    last_heard: i64
}

fn decide_next(in_progress: &HashMap<u64, Job>) -> Job {
    // check if master has been updated. if so, rewind time machine and send
    // out a job for master. else, use the time machine to decide what to do
    // next, given the history file and the in-progress jobs.
    Job {
        id: 42,
        commit: ~"7daea7c9c107238ba7bfc2e9f0e8955d42ad71ed",
        configure: ~"",
        make: ~"",
        last_heard: extra::time::get_time().sec,
    }
}

struct JobsIter {
    priv in_progress: HashMap<u64, Job>,
}

impl JobsIter {
    pub fn new() -> JobsIter {
        JobsIter {
            in_progress: HashMap::new()
        }
    }
}

impl Iterator<Job> for JobsIter {
    pub fn next(&mut self) -> Option<Job> {
        let x = decide_next(&self.in_progress);
        self.in_progress.insert(x.id, x.clone());
        Some(x)
    }
}

impl JobsIter {
    pub fn finish_job(&mut self, id: u64) {
        self.in_progress.pop(&id);
    }

    pub fn mut_ref<'a>(&'a mut self, id: u64) -> Option<&'a mut Job> {
        self.in_progress.find_mut(&id)
    }
}

fn main() {
    let context = zmq::Context::new();
    let publisher = context.socket(zmq::PUB).unwrap();
    publisher.bind("tcp://*:7538");
    let listener = context.socket(zmq::REP).unwrap();
    listener.bind("tcp://*:7539");

    let mut jobs = JobsIter::new();

    loop {
        let resp = match listener.recv_bytes(0) {
            Ok(x) => x,
            Err(x) => fail!("%?", x)
        };
        let mut msg = MemReader::new(resp);
        match msg.read_u8() {
            // "Give me a job!"
            0 => {
                listener.send(jobs.next().unwrap().to_bytes(true), 0);
            },
            // "I am working on that job!"
            1 => {
                let id = msg.read_le_u64();
                match jobs.mut_ref(id) {
                    Some(x) => x.last_heard = time::get_time().sec,
                    None => error!("client said it's working on a job with no entry")
                };
                listener.send(&[], 0);
            },
            // "Job finished, boss"
            2 => {
                let id = msg.read_le_u64();
                jobs.finish_job(id);
                listener.send(&[], 0);
            }
            _ => error!("invalid request id, dropping")
        }
    }
}
