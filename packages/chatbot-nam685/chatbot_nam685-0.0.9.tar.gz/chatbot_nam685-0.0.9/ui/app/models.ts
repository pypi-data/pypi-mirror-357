export class Thread {
  constructor(
    public thread_id: string,
    public status: string
  ) {}
}

export class HumanReview {
  constructor(
    public action: string,
    public data: string
  ) {}
}
