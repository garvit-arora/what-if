import argparse,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"services"/"api"))
from app.db.relate_repository import RelateRepository
from app.domains.history.seed import load_dataset,seed_history
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--database",type=Path,default=ROOT/"data"/"thread.rl");a=p.parse_args()
    data=load_dataset(ROOT/"data"/"seeds"/"napoleonic_history.json")
    with RelateRepository(a.database) as repo: print(seed_history(repo,data))
