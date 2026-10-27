#[derive(Debug, Clone)]
pub struct ScoreManager {
    pub winning_score: u32,
    pub p1_score: u32,
    pub p2_score: u32,
    pub winner: Option<u32>,
}

impl ScoreManager {
    pub fn new(winning_score: u32) -> Self {
        Self {
            winning_score: winning_score.max(1),
            p1_score: 0,
            p2_score: 0,
            winner: None,
        }
    }

    #[inline]
    pub fn is_game_over(&self) -> bool {
        self.winner.is_some()
    }

    pub fn add_point(&mut self, player: u32) -> bool {
        if self.is_game_over() {
            return true;
        }

        match player {
            1 => {
                self.p1_score += 1;
                if self.p1_score >= self.winning_score {
                    self.winner = Some(1);
                    return true;
                }
            }
            2 => {
                self.p2_score += 1;
                if self.p2_score >= self.winning_score {
                    self.winner = Some(2);
                    return true;
                }
            }
            _ => {}
        }

        false
    }

    pub fn reset(&mut self) {
        self.p1_score = 0;
        self.p2_score = 0;
        self.winner = None;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_score_progression_and_victory() {
        let mut sm = ScoreManager::new(5);
        assert!(!sm.is_game_over());

        for _ in 0..4 {
            assert!(!sm.add_point(1));
        }
        assert_eq!(sm.p1_score, 4);
        assert!(!sm.is_game_over());

        // 5th point triggers victory
        assert!(sm.add_point(1));
        assert!(sm.is_game_over());
        assert_eq!(sm.winner, Some(1));

        // Further points do nothing
        assert!(sm.add_point(2));
        assert_eq!(sm.p2_score, 0);

        sm.reset();
        assert!(!sm.is_game_over());
        assert_eq!(sm.p1_score, 0);
    }
}
